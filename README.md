# PAL_4G

4G 压力报警联动控制系统，当前仓库包含后端、Web 管理端和微信小程序三端代码。

## 项目结构

```text
PAL_4G/
├─ backend/        # 后端服务，FastAPI
├─ web/            # Web 管理端，Vue 3 + Vite
├─ miniprogram/    # 微信小程序端，UniApp + Vue 3
└─ docs/           # 项目文档与联调资料
```

## 本地端口

- 后端接口服务：`http://127.0.0.1:8001`
- 后端 Swagger：`http://127.0.0.1:8001/docs`
- Web 前端开发服务：`http://127.0.0.1:5173`

说明：

- Web 开发环境通过 Vite 代理把 `/api` 请求转发到 `http://127.0.0.1:8001`
- 小程序当前也对接同一套后端接口，接口前缀为 `/api/v1`
- 小程序开发联调时，服务端口仍是 `8001`；本机调试可指向本地地址，真机调试通常需改为可访问的 HTTPS 服务地址或隧道地址

## 需求完成情况对比

以下对比以需求文档 `docs/4G 压力报警模块 · 软件需求沟通文档.md` 为准，按当前仓库代码状态整理。

| 需求项 | 后端 | Web | 小程序 |
| --- | --- | --- | --- |
| 账号登录与权限区分 | 已完成。支持 `super_admin`、`manager`、`device_user`，含登录、当前用户、改密、重置密码等能力 | 已完成。登录页、角色路由、用户信息展示已接通 | 已完成。支持账号密码登录、登录态恢复、401 失效退出、微信登录入口与补绑定入口 |
| 设备状态查看 | 已完成。提供设备、模块、概览、详情、实时事件等接口 | 已完成。支持设备总览、设备列表、设备详情和状态展示 | 已完成。支持首页摘要、我的设备、设备详情与多模块状态查看 |
| 报警记录查询 | 已完成。支持查询、筛选、分页、恢复 | 已完成。支持报警列表、分页、跳页和筛选 | 已完成。支持报警分页、关键词、类型、日期筛选 |
| 报警联动断开 | 已完成。支持报警触发后按同一归属设备集生成联动命令并记录结果 | 已完成基础展示。可查看报警、命令和联动结果 | 已完成基础展示。首页、详情页、报警页可查看最近报警和命令结果 |
| 手动控制继电器 | 已完成。支持指令下发、执行反馈、补发 | 已完成。设备详情页可执行控制操作 | 已完成。设备详情页支持按模块远程控制继电器开关 |
| 设备绑定与移除 | 已完成。支持按 SN 绑定、解绑和归属变更 | 已部分完成。管理侧能力完整，普通用户闭环不作为当前重点 | 已完成。支持 SN 绑定、扫码填充、移除设备 |
| 超级管理员管理能力 | 已完成。支持用户、设备、分组、运维、调度等管理接口 | 已完成。已实现管理端主流程页面 | 未实现。按需求和当前定位，小程序仅面向普通设备账号 |
| 实时状态刷新 | 已完成。支持 WebSocket 事件、状态上报、反馈回写 | 已完成。支持实时状态提示与联动展示 | 已完成。首页、设备页、详情页接入 WebSocket，并保留轮询兜底 |
| 微信消息推送 | 已基本完成。已实现微信登录、绑定、订阅状态、订阅开关、报警通知派发链路 | 不涉及 | 已基本完成。已有订阅状态查询、订阅/退订入口，仍需真实模板和真机验收 |
| 真实设备通信接入 | 已具备基础能力。包含 MQTT 骨架、协议模板、状态/报警/反馈处理，但真实设备闭环仍需 Broker、现场参数和真报文确认 | 不涉及 | 不涉及 |
| 自动化测试 | 已完成。`pytest` 已接入 | 已完成。`Vitest` 与 `Playwright` 已接入 | 未完成。当前仍以微信开发者工具联调和真机测试为主 |

补充说明：

- 小程序当前已完成页面：登录、首页、我的设备、设备详情、设备绑定、报警、我的、设置。
- 小程序当前已对接真实接口，不再是骨架工程。
- 小程序当前主要剩余工作是：真机微信能力验收、小程序专用自动化测试、真实设备 MQTT 闭环联调。

## 小程序当前对接接口

小程序当前已接入以下后端接口：

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/wechat-login`
- `POST /api/v1/auth/wechat-bind`
- `GET /api/v1/dashboard/my/home`
- `GET /api/v1/dashboard/my/devices`
- `GET /api/v1/dashboard/my/alarms`
- `GET /api/v1/dashboard/alarms/page`
- `GET /api/v1/devices/{device_id}`
- `GET /api/v1/dashboard/devices/{device_id}`
- `POST /api/v1/relay-commands`
- `POST /api/v1/devices/bind`
- `POST /api/v1/devices/{device_id}/unbind`
- `POST /api/v1/users/me/change-password`
- `GET /api/v1/notifications/subscription-status`
- `POST /api/v1/notifications/subscribe`
- `POST /api/v1/notifications/unsubscribe`
- `GET /api/v1/ws/events`

## 启动说明

### 启动后端

```powershell
cd D:\project\code\PAL_4G\backend
D:\uv\venvs\pal_4g\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

如果要做小程序真机调试，建议改为：

```powershell
cd D:\project\code\PAL_4G\backend
D:\uv\venvs\pal_4g\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 启动 Web

```powershell
cd D:\project\code\PAL_4G\web
npm.cmd install
npm.cmd run dev
```

### 启动小程序开发

```powershell
cd D:\project\code\PAL_4G\miniprogram
npm.cmd install
```

然后使用 HBuilderX 或 UniApp CLI 编译到微信小程序，再在微信开发者工具中打开编译产物。

小程序接口说明：

- 小程序后端接口端口同样使用 `8001`
- 当前小程序配置支持通过 `SERVICE_ORIGIN` 动态拼接：
  - API：`{SERVICE_ORIGIN}/api/v1`
  - WebSocket：`{SERVICE_ORIGIN}/api/v1/ws/events`
- 如果是真机调试，`SERVICE_ORIGIN` 不应继续使用 `127.0.0.1`

## 环境变量

后端配置文件位于 `backend/.env`。如需接入真实 MQTT 或微信能力，至少补齐以下配置。

### MQTT

```env
MQTT_ENABLED=true
MQTT_BROKER_HOST=你的MQTT服务器地址
MQTT_BROKER_PORT=1883
MQTT_USERNAME=你的MQTT用户名
MQTT_PASSWORD=你的MQTT密码
MQTT_CLIENT_ID=pal_4g_backend
```

### 微信小程序

```env
WECHAT_ENABLED=true
WECHAT_LOGIN_USE_REAL_CODE2SESSION=true
WECHAT_APP_ID=你的小程序AppID
WECHAT_APP_SECRET=你的小程序AppSecret
WECHAT_SUBSCRIBE_TEMPLATE_ID=报警订阅消息模板ID
WECHAT_SUBSCRIBE_PAGE=pages/alarms/index
WECHAT_SUBSCRIBE_MINIPROGRAM_STATE=formal
WECHAT_SUBSCRIBE_LANG=zh_CN
WECHAT_SUBSCRIBE_FIELD_ALARM_TYPE=thing1
WECHAT_SUBSCRIBE_FIELD_DEVICE_NAME=thing2
WECHAT_SUBSCRIBE_FIELD_TRIGGER_TIME=time3
WECHAT_SUBSCRIBE_FIELD_REMARK=thing4
ALARM_NOTIFICATION_DISPATCH_INTERVAL_SECONDS=60
```

## 测试说明

### 后端测试

```powershell
cd D:\project\code\PAL_4G\backend
D:\uv\venvs\pal_4g\Scripts\python.exe -m pytest -q
```

### Web 单元测试

```powershell
cd D:\project\code\PAL_4G\web
npm.cmd run test
```

### Web 端到端测试

```powershell
cd D:\project\code\PAL_4G\web
npm.cmd run test:e2e
```

### 小程序测试建议

- 接口与服务逻辑：继续使用后端 `pytest`
- 小程序页面与交互：微信开发者工具联调
- 真机能力：真机预览 / 真机调试
- 若后续补自动化：优先考虑 `miniprogram-automator` 或 `uni-automator`

