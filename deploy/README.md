# PAL_4G Deploy

这个目录放当前项目部署时需要优先准备和修改的文件，基于现有代码、`docs/部署文档.md` 和 `docs/真机接入资料清单（硬件直接对接网站）.md` 整理。

## 文件说明

| 文件 | 用途 | 当前状态 |
| --- | --- | --- |
| `backend.env.production.example` | 后端生产环境变量模板 | 可直接复制后按真实值修改 |
| `web.env.production.example` | Web 生产环境变量模板 | 可直接用于构建 |
| `nginx.pal4g.conf` | Web + API + WebSocket 的 Nginx 反向代理模板 | 可直接作为起点，需替换域名和证书路径 |
| `pal4g-backend.service` | Linux systemd 托管后端模板 | 可直接作为起点，需替换用户、Python 路径、项目路径 |
| `emqx-docker-compose.yml` | EMQX Broker 启动模板 | 新增，适合作为 MQTT Broker 起步方案 |
| `emqx.env.example` | EMQX 基础环境变量模板 | 新增，需按服务器实际情况改值 |

## 部署人员必须替换的内容

### 1. 后端配置

以下项必须改成真实值，不能直接沿用模板：

| 配置项 | 为什么必须改 |
| --- | --- |
| `SECRET_KEY` | 默认值不安全 |
| `DEFAULT_ADMIN_PASSWORD` | 默认管理员密码不能直接上线 |
| `MQTT_BROKER_HOST` | 当前模板只是推荐域名 |
| `MQTT_BROKER_PORT` | 要和最终 Broker 实际端口一致 |
| `MQTT_USERNAME` | 当前是占位值 |
| `MQTT_PASSWORD` | 当前是占位值 |
| `MQTT_TLS_CA_CERTS` | 要替换成服务器真实证书路径 |
| `MQTT_TLS_SERVER_HOSTNAME` | 要和 Broker 真实域名一致 |
| `WECHAT_APP_ID` | 当前是占位值 |
| `WECHAT_APP_SECRET` | 当前是占位值 |
| `WECHAT_SUBSCRIBE_TEMPLATE_ID` | 当前是占位值 |

### 2. Web 配置

| 配置项 | 为什么必须确认 |
| --- | --- |
| `VITE_API_BASE` | 生产环境建议保留 `/api/v1`，如果网关路径不同要同步调整 |

### 3. Nginx 配置

以下内容当前都只是模板值：

| 配置项 | 当前值 | 部署时要改什么 |
| --- | --- | --- |
| `server_name` | `usr-iot.endpage.net` | 改成真实站点域名 |
| `ssl_certificate` | Let’s Encrypt 示例路径 | 改成真实证书路径 |
| `ssl_certificate_key` | Let’s Encrypt 示例路径 | 改成真实私钥路径 |
| `root` | `/var/www/pal4g/web/dist` | 改成实际 Web 静态目录 |

### 4. systemd 配置

以下内容必须按服务器环境调整：

| 配置项 | 当前值 | 部署时要改什么 |
| --- | --- | --- |
| `User` / `Group` | `www-data` | 改成实际运行用户 |
| `WorkingDirectory` | `/opt/pal4g/backend` | 改成项目真实路径 |
| `EnvironmentFile` | `/opt/pal4g/backend/.env` | 改成后端 `.env` 真实路径 |
| `ExecStart` | `/opt/pal4g/.venv/bin/python ...` | 改成服务器 Python/venv 真实路径 |

## 当前还没有、需要部署人员补齐的内容

这些内容仓库里没有现成最终值，部署时必须补：

| 类别 | 当前是否已有 | 还缺什么 |
| --- | --- | --- |
| 公网服务器 | 没有 | Linux 服务器或云主机 |
| 正式域名 | 没有 | 网站域名和 MQTT 子域名 |
| DNS 解析 | 没有 | 域名解析到公网 IP |
| HTTPS 证书 | 没有 | Web 站点证书 |
| MQTT TLS 证书 | 没有 | Broker TLS 证书链 |
| MQTT Broker 真实账号策略 | 没有 | 用户名、密码、ACL 策略 |
| 微信真实配置 | 没有 | `AppID`、`AppSecret`、模板 ID、字段映射 |
| 真实设备参数 | 没有 | SN、IMEI、现场 MQTT 配置、payload 样例 |
| 数据备份策略 | 没有 | SQLite 备份或迁移方案 |

## 当前项目已具备、可直接复用的内容

| 内容 | 当前状态 |
| --- | --- |
| 后端 API 服务代码 | 已具备 |
| Web 前端代码 | 已具备 |
| 小程序前端代码 | 已具备 |
| MQTT 接入逻辑 | 已具备 |
| MQTT TLS 配置能力 | 已具备 |
| WebSocket 实时推送 | 已具备 |
| 微信登录/绑定/订阅接口 | 已具备 |
| 部署模板目录 | 已具备本目录中的起步模板 |

## 推荐部署顺序

1. 准备 Linux 服务器、域名、DNS 和证书
2. 先部署 MQTT Broker，推荐从 `emqx-docker-compose.yml` 起步
3. 按 `backend.env.production.example` 填好后端生产配置
4. 安装后端依赖并用 `pal4g-backend.service` 托管
5. 构建 Web 并把静态文件部署到 Nginx 站点目录
6. 按 `nginx.pal4g.conf` 调整域名、证书和静态目录
7. 放开 `443`、`8883`，必要时临时放开 `1883`
8. 让真实设备改连自有 Broker，并按 `pal4g/devices/{device_sn}/...` 主题规范联调
9. 最后做 Web、API、MQTT 和真机验收

## 说明

- 当前项目默认数据库仍是 SQLite，生产前至少要明确备份策略。
- 当前 Broker 方案以 EMQX 为推荐起点，Mosquitto 只作为备选。
- 真正阻塞上线的通常不是后端代码，而是服务器、域名、证书、Broker 和真实设备参数。
