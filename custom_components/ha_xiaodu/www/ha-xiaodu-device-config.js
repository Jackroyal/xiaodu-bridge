/*!
 * ha_xiaodu 设备行菜单扩展（保留方案，注入式，带完整说明）
 *
 * 功能：在「设备与服务 → 小度中枢」展开的设备行三点菜单里，为每个设备
 * 追加「单元与能力」入口，点击打开只针对该设备的单元/能力编辑对话框。
 *
 * ── 为什么是注入实现 ──────────────────────────────────────────────
 * 「设备与服务」页的设备行由核心组件 ha-config-entry-device-row 渲染，
 * 其三点菜单是写死的：编辑 / 实体（有实体时）/ 禁用 / 移除设备。
 * 截至 HA 2026.8 前端，核心没有为"自定义菜单项"提供任何扩展口
 * （没有 manifest 字段、WS 钩子或回调），因此这个入口只能通过注入添加。
 *
 * 注入原理（三步）：
 *   1. 后端用官方 API frontend.add_extra_js_url() 把本模块注册进前端
 *      （HACS 注入 iconset 用的也是这个 API，属于官方注册途径）；
 *   2. 模块覆写 ha-config-entry-device-row 原型的 Lit updated()，
 *      在每次渲染完成后向 shadow DOM 里的 ha-dropdown 追加一个
 *      ha-dropdown-item（Lit 的 updated() 是官方生命周期，覆写安全）；
 *   3. 监听 ha-dropdown 的 wa-select 事件，拦截我们自定义的 value。
 *      核心自身的菜单处理器对未知 value 是 no-op，不会冲突。
 *   对话框数据与保存走自定义 WebSocket 命令 ha_xiaodu/device_config 与
 *   ha_xiaodu/set_device_config（这部分是正规的自定义集成后端 API）。
 *
 * ── 已知风险与降级 ────────────────────────────────────────────────
 * 往核心组件 DOM 里塞菜单项不是官方用途：HA 大版本升级若改变
 * ha-config-entry-device-row 的内部结构，本入口可能失效。所有操作都
 * 包在 try/catch + 存在性检查里，最坏情况只是菜单项不显示，
 * 不影响集成自身（设备同步、状态上报、选项流程均不依赖本模块）。
 *
 * ── 官方替代方案（供后续决策参考）────────────────────────────────
 * 1. 「设备与能力」选项流程：官方且稳定，入口在配置条目上
 *    （中枢 → 小度 → 设备 → 单元/能力），无需本模块。
 * 2. 自定义配置面板：官方机制（config_panel_domain，alarmo/HACS 同款），
 *    用自建前端面板整体替换集成配置页，可做到完全无注入，
 *    代价是工程量大，并会替换 HA 自带的集成详情页体验。
 * 3. 设备注册表 configuration_url：官方，但只出现在设备详情页，
 *    不出现在设备行菜单，只能作为辅助入口。
 *
 * 维护提示：升级 HA 后若发现菜单项消失，先查浏览器控制台是否有
 * "ha_xiaodu: 设备行菜单注入失败"；再检查核心组件模板是否变化。
 */

const MENU_VALUE = "ha_xiaodu_device_config";
const DOMAIN = "ha_xiaodu";

const CAP_LABELS = {
  power: "开关",
  brightness: "亮度",
  colorTemperature: "色温",
  color: "颜色",
  volume: "音量",
  channel: "频道",
  mute: "静音",
  fanSpeed: "风速",
  targetTemperature: "目标温度",
  targetHumidity: "目标湿度",
  mode: "模式",
  suction: "吸力",
  continue: "继续",
  temperature: "温度",
  humidity: "湿度",
};

/* ------------------------- 设备行菜单注入 ------------------------- */

/**
 * 给单行设备行补菜单项。
 * 只处理 ha_xiaodu 域名下的设备行；guard 顺序：
 *   1. 菜单项已存在（避免重复插入）；
 *   2. 本 dropdown 已处理过（避免同一元素上累积多个 wa-select 监听）。
 * Lit 重渲染时若整体替换了 dropdown 元素，标志位随之消失，会重新补项；
 * 若元素复用，标志位避免重复监听。两种路径都能自愈。
 */
function patchRowMenu(row) {
  if (!row.entry || row.entry.domain !== DOMAIN) {
    return;
  }
  const root = row.shadowRoot;
  if (!root) {
    return;
  }
  const dropdown = root.querySelector("ha-dropdown");
  if (!dropdown || dropdown.querySelector(`ha-dropdown-item[value="${MENU_VALUE}"]`)) {
    return;
  }
  if (dropdown.__ha_xiaodu_menu_patched) {
    return;
  }
  dropdown.__ha_xiaodu_menu_patched = true;

  const item = document.createElement("ha-dropdown-item");
  item.setAttribute("value", MENU_VALUE);
  item.innerHTML = '<ha-icon slot="icon" icon="mdi:tune"></ha-icon>单元与能力';
  dropdown.appendChild(item);

  // 核心的 _handleMenuAction 对未知 value 直接 return（no-op），
  // 因此这里先让核心处理（无副作用），再拦截我们的 value 打开对话框。
  dropdown.addEventListener("wa-select", (ev) => {
    const value = ev.detail && ev.detail.item && ev.detail.item.value;
    if (value !== MENU_VALUE) {
      return;
    }
    ev.stopImmediatePropagation();
    const device = row.device;
    // 我们注册的设备标识是 (DOMAIN, 底层 device_key)，
    // 从 identifiers 里还原 device_key 才能查询/保存配置。
    const identifier = (device.identifiers || []).find(
      ([domain]) => domain === DOMAIN
    );
    if (!identifier) {
      return;
    }
    openDialog(row.hass, identifier[1], device.name);
  });
}

/**
 * 覆写核心组件原型的 Lit updated() 生命周期。
 * updated() 在每次渲染提交后触发，此时 shadow DOM 已更新完毕，
 * 是最可靠的安全插入时机。通过微任务再往后推一拍，避免和渲染竞争。
 * 只做一次覆写（__ha_xiaodu_patched 防重）。
 */
function patchDeviceRowClass() {
  if (!customElements.get("ha-config-entry-device-row")) {
    return;
  }
  const proto = customElements.get("ha-config-entry-device-row").prototype;
  if (proto.__ha_xiaodu_patched) {
    return;
  }
  proto.__ha_xiaodu_patched = true;
  const origUpdated = proto.updated;
  proto.updated = function (changedProperties) {
    if (origUpdated) {
      origUpdated.call(this, changedProperties);
    }
    // 渲染完成后补菜单项；异常只记录，不影响行组件本身。
    queueMicrotask(() => {
      try {
        patchRowMenu(this);
      } catch (err) {
        console.error("ha_xiaodu: 设备行菜单注入失败", err);
      }
    });
  };
}

function openDialog(hass, deviceKey, deviceName) {
  let dialog = document.querySelector("ha-xiaodu-device-config-dialog");
  if (!dialog) {
    dialog = document.createElement("ha-xiaodu-device-config-dialog");
    document.body.appendChild(dialog);
  }
  dialog.hass = hass;
  dialog.open(deviceKey, deviceName);
}

/* ----------------------- 单元/能力编辑对话框 ----------------------- */

/**
 * 单设备单元/能力编辑器。
 * 数据来源：ha_xiaodu/device_config（读：可用单元、可选能力、必选能力、
 * 当前启用状态）。
 * 保存：ha_xiaodu/set_device_config（写，后端要求管理员权限）。
 * 语义与配置流程一致：启用单元 = options.devices[device_key] 里保留该
 * entity_id；必选能力（如开关）由后端强制补回；全部单元取消勾选会把该
 * 设备移出同步。
 */
class HaXiaoduDeviceConfigDialog extends HTMLElement {
  connectedCallback() {
    if (!this.shadowRoot) {
      this.attachShadow({ mode: "open" });
    }
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          --dialog-content-padding: 8px 24px 20px;
          --mdc-dialog-min-width: 520px;
        }
        .unit {
          border: 1px solid var(--divider-color);
          border-radius: var(--ha-card-border-radius, 12px);
          padding: 12px 16px;
          margin-bottom: 12px;
        }
        .unit-name {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 500;
          margin-bottom: 10px;
        }
        .unit-name .default-badge {
          font-size: 12px;
          color: var(--primary-color);
          border: 1px solid currentColor;
          border-radius: 999px;
          padding: 0 8px;
          opacity: 0.85;
        }
        .caps {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
          gap: 2px 12px;
          margin-top: 4px;
        }
        .hint {
          color: var(--secondary-text-color);
          font-size: 12px;
          margin: 4px 0 16px;
        }
        .empty {
          color: var(--secondary-text-color);
          padding: 24px 0;
          text-align: center;
        }
        .error {
          color: var(--error-color);
          white-space: pre-wrap;
          padding: 16px 0;
        }
        .loading {
          padding: 24px 0;
          text-align: center;
          color: var(--secondary-text-color);
        }
      </style>
      <ha-dialog open>
        <ha-dialog-header show-back-button>
          <span slot="title" id="dialog-title">单元与能力</span>
        </ha-dialog-header>
        <div dialog-content id="content"></div>
        <mwc-button slot="secondary-action" id="cancel">取消</mwc-button>
        <mwc-button
          slot="primary-action"
          id="save"
          disabled
        >保存</mwc-button>
      </ha-dialog>
    `;
    this.shadowRoot
      .querySelector("ha-dialog")
      .addEventListener("closed", () => this._onClosed());
    this.shadowRoot
      .querySelector("ha-dialog-header")
      .addEventListener("back-click", () => this._onClosed());
    this.shadowRoot.querySelector("#cancel").addEventListener("click", () =>
      this.close()
    );
    this.shadowRoot.querySelector("#save").addEventListener("click", () =>
      this._save()
    );
  }

  set hass(value) {
    this._hass = value;
  }

  async open(deviceKey, deviceName) {
    this._deviceKey = deviceKey;
    const title = this.shadowRoot.querySelector("#dialog-title");
    const content = this.shadowRoot.querySelector("#content");
    const save = this.shadowRoot.querySelector("#save");
    title.textContent = `单元与能力 · ${deviceName}`;
    content.innerHTML = `<div class="loading">正在读取设备配置…</div>`;
    save.disabled = true;
    try {
      const result = await this._hass.callWS({
        type: "ha_xiaodu/device_config",
        device_key: deviceKey,
      });
      this._state = result.device;
      this._render();
      save.disabled = false;
    } catch (err) {
      content.innerHTML = `<div class="error">读取失败：${err.message || err}</div>`;
    }
  }

  _render() {
    const content = this.shadowRoot.querySelector("#content");
    const device = this._state;
    const sections = device.units.map((unit) => {
      const selectable = unit.selectable
        .map((capability) => {
          const checked = unit.enabled_capabilities.includes(capability);
          const label = CAP_LABELS[capability] || capability;
          return `
            <ha-formfield label="${label}">
              <ha-checkbox data-cap="${capability}" ${checked ? "checked" : ""}>
              </ha-checkbox>
            </ha-formfield>`;
        })
        .join("");
      const required = unit.required
        .map((capability) => {
          const label = CAP_LABELS[capability] || capability;
          return `
            <ha-formfield label="${label}（必选）">
              <ha-checkbox data-required-cap="${capability}" checked disabled>
              </ha-checkbox>
            </ha-formfield>`;
        })
        .join("");
      const badge = unit.is_default
        ? '<span class="default-badge">默认</span>'
        : "";
      return `
        <div class="unit" data-entity="${unit.entity_id}">
          <div class="unit-name">
            <ha-formfield label="${unit.name}">
              <ha-checkbox class="unit-toggle" ${
                unit.enabled ? "checked" : ""
              }></ha-checkbox>
            </ha-formfield>
            ${badge}
          </div>
          <div class="caps">
            ${selectable}${required}
          </div>
        </div>`;
    });
    content.innerHTML = `
      <div class="hint">
        ${device.area_name ? `${device.area_name} · ` : ""}${device.name}，共
        ${device.units.length} 个单元。取消勾选所有单元会将该设备移出同步。
      </div>
      ${sections.join("") || '<div class="empty">该设备没有可配置的单元</div>'}
    `;
    this._bindToggles();
  }

  _bindToggles() {
    this.shadowRoot.querySelectorAll(".unit").forEach((section) => {
      const toggle = section.querySelector(".unit-toggle");
      const caps = section.querySelector(".caps");
      const update = () => {
        caps.style.opacity = toggle.checked ? "1" : "0.45";
        caps.style.pointerEvents = toggle.checked ? "auto" : "none";
      };
      toggle.addEventListener("change", update);
      update();
    });
  }

  async _save() {
    const save = this.shadowRoot.querySelector("#save");
    save.disabled = true;
    const units = {};
    this.shadowRoot.querySelectorAll(".unit").forEach((section) => {
      const enabled = section.querySelector(".unit-toggle").checked;
      if (!enabled) {
        return;
      }
      const capabilities = [];
      section
        .querySelectorAll('ha-checkbox[data-cap]')
        .forEach((checkbox) => {
          if (checkbox.checked) {
            capabilities.push(checkbox.dataset.cap);
          }
        });
      units[section.dataset.entity] = capabilities;
    });
    try {
      await this._hass.callWS({
        type: "ha_xiaodu/set_device_config",
        device_key: this._deviceKey,
        units,
      });
      this.close();
    } catch (err) {
      const content = this.shadowRoot.querySelector("#content");
      content.innerHTML +=
        `<div class="error">保存失败：${err.message || err}</div>`;
      save.disabled = false;
    }
  }

  _onClosed() {
    this.remove();
  }

  close() {
    const dialog = this.shadowRoot.querySelector("ha-dialog");
    if (dialog) {
      dialog.close();
    } else {
      this.remove();
    }
  }
}

/* ----------------------------- 启动 ----------------------------- */

try {
  patchDeviceRowClass();
  customElements.whenDefined("ha-config-entry-device-row").then(patchDeviceRowClass);
  if (!customElements.get("ha-xiaodu-device-config-dialog")) {
    customElements.define("ha-xiaodu-device-config-dialog", HaXiaoduDeviceConfigDialog);
  }
} catch (err) {
  console.error("ha_xiaodu: 前端模块初始化失败", err);
}
