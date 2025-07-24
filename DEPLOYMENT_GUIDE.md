# 🚀 跨境电商智能决策系统部署指南

## 📋 部署方案对比

| 部署方式 | 成本 | 难度 | 适用场景 | 推荐指数 |
|---------|------|------|----------|----------|
| **Streamlit Cloud** | 免费 | ⭐ | 演示、测试 | ⭐⭐⭐⭐⭐ |
| **Heroku** | $7/月起 | ⭐⭐ | 小型应用 | ⭐⭐⭐⭐ |
| **Docker + VPS** | $5-20/月 | ⭐⭐⭐ | 生产环境 | ⭐⭐⭐⭐⭐ |
| **AWS/Azure/GCP** | $10-50/月 | ⭐⭐⭐⭐ | 企业级 | ⭐⭐⭐⭐ |

---

## 🌟 方案一：Streamlit Cloud (推荐新手)

### 优势
- ✅ 完全免费
- ✅ 零配置部署
- ✅ 自动 HTTPS
- ✅ 官方支持

### 部署步骤

#### 1. 准备 GitHub 仓库
```bash
# 初始化 Git 仓库
git init
git add .
git commit -m "Initial commit: Cross-border E-commerce System"

# 推送到 GitHub
git remote add origin https://github.com/yourusername/cross-border-ecommerce.git
git branch -M main
git push -u origin main
```

#### 2. 部署到 Streamlit Cloud
1. 访问 [share.streamlit.io](https://share.streamlit.io)
2. 使用 GitHub 账号登录
3. 点击 "New app"
4. 选择您的仓库
5. 设置主文件路径: `跨境电商/app.py`
6. 点击 "Deploy!"

#### 3. 访问应用
- 部署完成后会获得一个 `.streamlit.app` 域名
- 例如: `https://your-app-name.streamlit.app`

---

## 🐳 方案二：Docker 部署 (推荐生产)

### 优势
- ✅ 环境一致性
- ✅ 易于扩展
- ✅ 完全控制
- ✅ 支持自定义域名

### 本地 Docker 部署

```bash
# 1. 构建镜像
docker build -t cross-border-ecommerce .

# 2. 运行容器
docker run -d \
  --name cross-border-ecommerce \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  cross-border-ecommerce

# 3. 访问应用
# http://localhost:8501
```

### 云服务器部署

#### 1. 购买云服务器
推荐配置：
- **CPU**: 2核心
- **内存**: 4GB
- **存储**: 40GB SSD
- **带宽**: 5Mbps

推荐服务商：
- 阿里云 ECS
- 腾讯云 CVM
- AWS EC2
- DigitalOcean Droplet

#### 2. 服务器环境配置
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重启以应用权限更改
sudo reboot
```

#### 3. 部署应用
```bash
# 克隆代码
git clone https://github.com/yourusername/cross-border-ecommerce.git
cd cross-border-ecommerce/跨境电商

# 使用部署脚本
chmod +x deploy.sh
./deploy.sh cloud

# 或手动部署
docker-compose up -d
```

#### 4. 配置域名和 SSL
```bash
# 安装 Nginx
sudo apt install nginx -y

# 复制 Nginx 配置
sudo cp nginx.conf /etc/nginx/sites-available/cross-border-ecommerce
sudo ln -s /etc/nginx/sites-available/cross-border-ecommerce /etc/nginx/sites-enabled/

# 安装 Certbot (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx -y

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# 重启 Nginx
sudo systemctl restart nginx
```

---

## ☁️ 方案三：云平台部署

### Heroku 部署

#### 1. 创建 Procfile
```bash
echo "web: streamlit run 跨境电商/app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
```

#### 2. 部署到 Heroku
```bash
# 安装 Heroku CLI
# 访问 https://devcenter.heroku.com/articles/heroku-cli

# 登录 Heroku
heroku login

# 创建应用
heroku create your-app-name

# 部署
git push heroku main

# 打开应用
heroku open
```

### AWS 部署 (使用 ECS)

#### 1. 推送镜像到 ECR
```bash
# 创建 ECR 仓库
aws ecr create-repository --repository-name cross-border-ecommerce

# 获取登录令牌
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# 构建并推送镜像
docker build -t cross-border-ecommerce .
docker tag cross-border-ecommerce:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/cross-border-ecommerce:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/cross-border-ecommerce:latest
```

#### 2. 创建 ECS 服务
- 使用 AWS 控制台创建 ECS 集群
- 创建任务定义
- 创建服务并配置负载均衡器

---

## 🔧 环境变量配置

创建 `.env` 文件：
```bash
# 应用配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 数据库配置 (如果使用)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# 安全配置
SECRET_KEY=your-secret-key-here

# 第三方服务配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## 📊 性能优化

### 1. 缓存配置
```python
# 在 app.py 中添加
import streamlit as st

# 配置页面
st.set_page_config(
    page_title="跨境电商智能决策系统",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 启用缓存
@st.cache_data(ttl=3600)  # 缓存1小时
def load_data():
    # 数据加载逻辑
    pass
```

### 2. 资源限制
```yaml
# docker-compose.yml 中添加
services:
  streamlit-app:
    # ... 其他配置
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

---

## 🔒 安全配置

### 1. 防火墙设置
```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. 定期备份
```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz data/
aws s3 cp backup_$DATE.tar.gz s3://your-backup-bucket/
rm backup_$DATE.tar.gz
EOF

# 添加到 crontab (每天凌晨2点备份)
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

---

## 📈 监控和日志

### 1. 应用监控
```bash
# 安装监控工具
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  prom/prometheus

docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

### 2. 日志管理
```bash
# 查看应用日志
docker logs cross-border-ecommerce

# 实时查看日志
docker logs -f cross-border-ecommerce

# 日志轮转配置
docker run --log-driver=json-file --log-opt max-size=10m --log-opt max-file=3
```

---

## 🆘 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看端口占用
sudo netstat -tlnp | grep :8501

# 杀死占用进程
sudo kill -9 <PID>
```

#### 2. 内存不足
```bash
# 查看内存使用
free -h

# 增加 swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 3. 依赖包问题
```bash
# 重新安装依赖
pip install --force-reinstall -r requirements.txt

# 清理 pip 缓存
pip cache purge
```

---

## 📞 技术支持

如果在部署过程中遇到问题，请：

1. 检查系统日志
2. 查看错误信息
3. 参考故障排除部分
4. 联系技术支持

**部署成功后，您将拥有一个功能完整的跨境电商智能决策系统！** 🎉
