# CyreneSimulator 接口文档

本文档基于现有代码库自动整理，包含了用户认证、聊天交互及管理员管理相关的 API 接口。

## 1. 用户认证模块 (User Auth)
**Base Path:** `/user_auth`

| 方法 | 路径 | 描述 | 请求参数 (主要) | 响应/备注 |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/captcha` | 获取图形验证码 | 无 | 返回图片流 (image/png), Headers包含 `X-Captcha-ID` |
| `POST` | `/register` | 用户注册 | `user_name`, `user_password`, `captcha_id`, `captcha_code` | `msg`, `user_id`, `user_name` |
| `POST` | `/login` | 用户登录 | `username` (Form表单), `password` (Form表单) | `access_token`, `token_type`, `user_id`, `user_name` |

## 2. 聊天交互模块 (Conversation)
**Base Path:** `/` (无前缀)

| 方法 | 路径 | 描述 | 请求参数 (主要) | 响应/备注 |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/create_chat` | 创建新对话 | `character_name`, `chat_name` | `chat_id`, `chat_name`, `character_name` |
| `POST` | `/send_message` | 发送消息 (流式) | `chat_id`, `message`, `model` | **Streaming Response** (text/plain) |
| `POST` | `/get_character_name` | 获取角色列表 | `page_size`, `page_number` | 角色列表数组 (支持缓存) |
| `POST` | `/get_current_user_conversation` | 获取当前用户会话列表 | `page_size`, `page_number` | 会话列表数组 (支持缓存) |
| `POST` | `/get_chat_history` | 获取聊天记录 | `chat_id` | `history_chat` (JSON 数组) |

## 3. 管理员管理模块 (Admin)
**Base Path:** `/admin`
*需要管理员权限 (`is_admin=True`)*

| 方法 | 路径 | 描述 | 请求参数 (主要) | 响应/备注 |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/create_user` | 创建用户 (管理员) | `user_name`, `user_password` | `user_id`, `user_name` |
| `POST` | `/soft_delete` | 软删除用户 | `user_id` | `msg`, `user_id` |
| `POST` | `/undo_soft_delete` | 撤销软删除 | `user_id` | `msg`, `user_id` |
| `DELETE` | `/true_delete` | 彻底删除用户 | `user_id` | **谨慎操作** |
| `POST` | `/ban` | 封禁用户 | `user_id` | `msg`, `user_id` |
| `POST` | `/unban` | 解封用户 | `user_id` | `msg`, `user_id` |
| `POST` | `/all_user` | 获取所有用户列表 | `page_size`, `page_number` | 用户列表数组 |
| `POST` | `/all_user_conversation` | 获取所有用户会话 | `page_size`, `page_number` | 会话列表数组 |
| `POST` | `/create_character` | 创建角色 | `character_name`, `system_prompt` | `character_id`, `character_name` |
| `POST` | `/delete_character` | 删除角色 | `character_id` | `msg`, `character_id` |
| `POST` | `/get_chat_history` | 管理员获取聊天记录 | `chat_id` | `history_chat` |

## 数据结构参考 (Schemas)

> 详细字段请参考代码目录 `schemas/` 下的 Pydantic 模型定义。

- **UserRegisterRequest**: `user_name`, `user_password`, `captcha_id`, `captcha_code`
- **MessageRequest**: `chat_id`, `message`, `model` (e.g. "gemini-pro"), `character_name`
