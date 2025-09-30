# File-Chain 项目说明

## 📖 项目简介

**File-Chain** 是一个结合 **区块链 + 加密技术** 的安全文件存储与共享平台。

* 项目的目标是确保文件在 **上传、存储、访问、共享** 全生命周期中的 **安全性、可追溯性和防篡改性**。
* 通过 **ECC（椭圆曲线加密）** 和 **ECDSA（数字签名）** 提供文件加密与签名能力；
* 结合 **区块链** 记录文件元信息、访问申请与审批过程，实现透明与不可篡改；
* 文件实际存储在 **云端（AWS EC2）**，而解密与验签流程则在 **用户本地程序** 中完成，从而兼顾了性能与安全性。

---

## 📌 项目流程

1. **用户注册**

   * 注册时生成用户的 **ECC**（加密用）和 **ECDSA**（签名用）的公私钥对。
   * **公钥**存储到数据库，**私钥**由用户自行保存。
   * 登录后才能进行后续操作。

2. **文件上传**

   * 上传者即文件的拥有者。
   * 流程：签名 → 加密 → 上传到 AWS EC2 → 元信息写入区块链。

3. **文件访问**

   * 用户可以查询并下载加密文件，但无法直接查看明文。

4. **访问申请**

   * 需要访问文件时，用户可向文件拥有者发起申请，相关信息写入区块链。

5. **审批流程**

   * 文件拥有者可审批请求：

     * **同意** → 提供自身 ECC 公钥与经 ECC 加密的 AES 密钥；
     * **拒绝** → 请求关闭。
   * 审批结果写入区块链。

6. **解密与验签（本地单机程序）**

   * 申请者获得加密文件 + 拥有者 ECC 公钥 + AES 密钥（加密），在本地执行：

     * 使用 ECC 解密 AES 密钥 → 解密文件；
     * 使用 ECDSA 公钥完成文件验签。

---

## 📂 项目目录结构

```bash
file-chain
├─ requirements.txt          # 项目依赖库
├─ uploads                   # 本地文件上传存储目录
└─ app
   ├─ db.py                  # 数据库连接和会话管理
   ├─ main.py                # 项目入口，FastAPI 启动文件
   │
   ├─ api                    # API 层，处理路由和请求
   │  ├─ auth.py             # 登录、注册、JWT 认证相关接口
   │  ├─ file.py             # 文件上传、查询相关接口
   │  └─ request.py          # 文件访问申请、审批相关接口
   │
   ├─ core                   # 核心功能层
   │  ├─ config.py           # 全局配置项（数据库、密钥等）
   │  ├─ crypto.py           # 加密、解密、签名等工具函数
   │  └─ security.py         # JWT 生成与验证，用户认证
   │
   ├─ models                 # ORM 模型（数据库表映射）
   │  ├─ file.py             # 文件表定义
   │  ├─ request.py          # 申请表定义
   │  └─ user.py             # 用户表定义
   │
   ├─ schemas                # 数据模型（Pydantic Schema，用于接口请求/响应校验）
   │  ├─ file.py             # 文件相关 Schema
   │  ├─ request.py          # 文件申请相关 Schema
   │  └─ user.py             # 用户相关 Schema
   │
   ├─ script                 
   │  └─ database.sql        # 数据库初始化脚本
   │
   └─ services               # 服务层，业务逻辑
      ├─ file_service.py     # 文件上传/查询逻辑
      ├─ request_service.py  # 文件申请/审批逻辑
      └─ user_service.py     # 用户注册/登录逻辑

```

---

## 🚀 启动 & 测试

### 1️⃣ 项目环境准备

* **Python 3.10+**
* **MySQL 8.0+**
* **接口测试工具**（Postman 或 Swagger UI: `http://127.0.0.1:8000/docs`）

安装依赖：

```bash
pip install -r requirements.txt
```


### 2️⃣ 数据库配置

修改 `app/core/config.py` 里的数据库连接，例如：

```python
DB_URL: str = "mysql+pymysql://username:password@localhost:3306/file_chain"
```

> ⚠️ 请根据你本地数据库的实际用户名(username)、密码(password)进行修改。


### 3️⃣ 初始化数据库

执行位于 `/app/script/database.sql` 的 SQL 脚本，创建相关表结构。


### 4️⃣ 启动服务

```bash
uvicorn app.main:app --reload
```


### 5️⃣ 验证服务

访问：

```
http://127.0.0.1:8000
```

返回：

```json
{"message": "Welcome to my Demo!"}
```


### 6️⃣ 接口测试

1. 在 Postman 中 **注册用户**
2. 登录成功后获取 `access_token`
3. 在 **Authorization → Bearer Token** 粘贴 `access_token`
4. 访问需要鉴权的接口，即可完成测试

---

## 🤝 协作规范

* **分支管理**

  * 基于 `master` 创建个人分支：

    ```
    dev-YourName
    ```
  * 在个人分支开发，不要直接在 master 上修改。

* **代码合并**

  * 开发完成 → 提交 PR 到 `master`；
  * 由 **Yuhao** 审核；
  * 合并前先拉取 master 到自己的分支，解决冲突后再合并。

* **任务分工**

  * 基础框架已搭建并可测试；
  * 部分功能未实现，代码中已标记 `TODO`；
  * 开发者需完成自己负责的 `TODO` 模块。

* **沟通**

  * 有任何问题请联系 **Yuhao**。

