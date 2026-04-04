# Web 端第二期开发计划

## Summary

第二期目标是从首期 MVP 过渡到“可运营、可管理、可维护”的正式后台，补齐首期明确排除的能力：用户管理、设备分组管理、设备归属分配、日志中心、调度任务页、MQTT 状态页、导出页、复杂运维页，以及国际化、深色模式、WebSocket 实时通信。

建议第二期按 **5 周** 推进，前提是首期核心链路已稳定、前后端联调基线已可用。第二期交付重点不是再扩展基础业务闭环，而是把系统提升到“管理员可用、运维可排障、业务可审计、体验可扩展”的阶段。

## Key Changes

### 第 1 周：管理员体系与设备管理增强
- 新增用户管理页面，覆盖用户列表、创建用户、编辑角色、启停用、重置密码。
- 新增设备归属分配能力，支持管理员为设备分配/回收 owner。
- 新增设备分组管理页面，支持分组列表、新建、编辑、删除、查看分组下设备。
- 新增设备与分组绑定能力，支持将设备加入或移出联动分组。
- 菜单按角色正式拆分：`super_admin` 可见管理与运维菜单，普通业务账号仅保留业务菜单。

依赖接口：
- `/api/v1/users`
- `/api/v1/users/{user_id}`
- `/api/v1/users/{user_id}/reset-password`
- `/api/v1/devices/groups`
- `/api/v1/devices/{device_id}/assign-owner`
- `/api/v1/devices/{device_id}/assign-group`
- `/api/v1/devices/{device_id}/unbind`

### 第 2 周：日志中心与导出能力
- 新增日志中心，拆分运行日志、操作日志、通信日志三个子视图。
- 支持分页、筛选、时间范围查询、关键字段高亮。
- 新增导出入口，覆盖报警导出与指令导出。
- 统一“审计视角”交互：从设备详情、报警记录、控制记录跳转到对应日志筛选结果。
- 对管理员提供只读审计视图，不在前端做日志修改动作。

依赖接口：
- `/api/v1/logs/runtime`
- `/api/v1/logs/runtime/page`
- `/api/v1/logs/operations`
- `/api/v1/logs/operations/page`
- `/api/v1/logs/communication`
- `/api/v1/logs/communication/page`
- `/api/v1/logs/overview`
- `/api/v1/dashboard/alarms/export`
- `/api/v1/dashboard/commands/export`

### 第 3 周：调度任务页、MQTT 状态页、运维首页
- 新增调度任务页，展示调度器状态、任务列表、最近执行记录。
- 提供管理员手动触发入口：离线检测、补发扫描、告警恢复检查、文件清理、数据库备份。
- 新增 MQTT 状态页，展示连接状态、基础配置摘要、模拟入口状态说明。
- 新增轻量运维首页，汇总调度状态、MQTT 状态、日志概览、最近备份。
- 保持第二期运维能力为“查看 + 受控触发”，不做复杂集群运维设计。

依赖接口：
- `/api/v1/jobs/scheduler`
- `/api/v1/jobs/history`
- `/api/v1/jobs/offline-check`
- `/api/v1/jobs/retry-pending`
- `/api/v1/jobs/alarm-recovery-check`
- `/api/v1/jobs/cleanup-files`
- `/api/v1/jobs/backup-database`
- `/api/v1/jobs/backups`
- `/api/v1/mqtt/status`
- `/api/v1/logs/overview`

### 第 4 周：实时能力、体验增强与主题/语言支持
- 为仪表盘、设备详情、报警记录、命令状态引入 WebSocket 实时更新；轮询保留为降级方案。
- 增加实时事件接入层，统一处理连接状态、重连、订阅、消息分发与页面同步。
- 增加深色模式，覆盖主布局、图表、表格、表单、状态标签与弹窗。
- 增加国际化基础框架，至少支持 `zh-CN` 与 `en-US` 两套资源，首期页面全部接入文案字典。
- 将导出、日志、调度、MQTT 页面一并接入主题与国际化体系，避免后补成本。

说明：
- 若后端当期没有 WebSocket 能力，第二期前半段先定义前端事件模型与适配层，并将 WebSocket 列为第二期上线阻塞项之一。
- 深色模式与国际化必须做成全局能力，不允许页面各自散落实现。

### 第 5 周：系统收口、权限回归与上线准备
- 全量回归管理员菜单、普通用户菜单、设备管理、日志查询、任务触发、导出下载、实时刷新、主题切换、语言切换。
- 整理第二期操作手册：管理员使用说明、运维排障说明、导出说明。
- 补齐前端埋点与错误监控接入点，至少覆盖页面崩溃、接口失败、WebSocket 断连。
- 输出第二期上线检查清单和第三期候选项。

## Public Interfaces / Types

### 新增或正式纳入前端的后端接口域
- 用户管理域：用户列表、详情、更新、重置密码。
- 设备管理增强域：设备分组、设备归属、设备分组分配。
- 日志与审计域：运行日志、操作日志、通信日志、日志总览。
- 运维域：调度状态、任务历史、手动触发任务、备份列表。
- MQTT 域：MQTT 客户端状态。
- 导出域：报警导出、指令导出。

### 前端新增核心类型
- `UserRead` / `UserCreate` / `UserUpdate`
- `DeviceGroupRead` / `DeviceGroupCreate` / `DeviceGroupUpdate`
- `SchedulerStatus` / `JobExecutionLogRead`
- `RuntimeLogPage` / `OperationLogPage` / `CommunicationLogPage`
- `LogsOverview`
- `MqttClientStatus`
- 实时事件基础类型：`RealtimeEvent`, `AlarmUpdatedEvent`, `CommandUpdatedEvent`, `DeviceUpdatedEvent`
- 全局 UI 类型：`LocaleCode`, `ThemeMode`

### 前置约束
- 第二期默认不要求新增 REST API 结构性改造，但 WebSocket 若缺失，需要后端补一个稳定事件通道。
- 导出能力以浏览器下载文件为默认交互，不新增前端二次加工逻辑。
- 主题和国际化为横切能力，必须贯穿全站。

## Test Plan

### 功能测试
- 用户管理：创建、编辑、禁用、重置密码。
- 设备分组：新建、编辑、删除、设备分配、权限校验。
- 设备归属：分配 owner、解绑 owner、列表状态同步。
- 日志中心：三类日志分页、筛选、跳转联动。
- 导出：报警导出、命令导出、下载成功与失败提示。
- 调度任务：任务列表展示、历史查看、手动触发、备份列表查看。
- MQTT 状态：连接状态展示、异常提示。
- 国际化：中英文切换后页面文案与时间/数字格式符合预期。
- 深色模式：主题切换后布局、图表、表格、弹窗均正确显示。
- WebSocket：连接成功、断线重连、事件落地、页面实时刷新。

### 权限与回归测试
- `super_admin` 可访问全部第二期页面。
- 非 `super_admin` 不可见管理员/运维菜单，直链访问返回前端拒绝并正确兜底。
- 首期页面功能不被第二期改动破坏。
- WebSocket 不可用时，关键页面可回退到轮询模式。

### 验收标准
- 第二期页面在管理员视角下完整可用。
- 日志、导出、调度、MQTT 页面全部具备稳定空态、错误态、权限兜底。
- 实时更新、深色模式、国际化三项横切能力至少覆盖首期与第二期核心页面。
- 管理、审计、运维三条链路可独立演示。

## Assumptions

- 首期 MVP 已完成并稳定，页面结构、状态管理、接口层可继续扩展。
- 后端现有管理与运维接口保持可用。
- WebSocket 为第二期新增依赖能力；若后端尚未提供，需要将其纳入第二期联动开发前提。
- 国际化第二期只要求中英文，不扩展更多语言。
- 深色模式第二期只要求全站视觉一致，不追求多品牌主题系统。
- 复杂运维页在第二期定义为“管理员运维面板”，不包含多节点、集群、高可用编排等更高级能力。
