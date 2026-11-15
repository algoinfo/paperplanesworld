# 纸飞机机库 · Folding Hangar

纯静态网页，复刻 [Fold'N Fly](https://www.foldnfly.com/) 机库中的 **58** 种纸飞机叠法（含逐步图解）。

## 本地打开

```bash
cd site
python3 -m http.server 8080
```

浏览器访问：http://localhost:8080

> 因使用 `fetch` 加载 `data/planes.json`，请用本地服务器打开，不要直接双击 `index.html`。

重新生成机型 SEO 页：

```bash
python3 scripts/build_seo_pages.py
```

部署到正式域名时，先在 `scripts/build_seo_pages.py` 里设置 `BASE_URL`，再重新生成，以便 canonical / sitemap / Open Graph 使用绝对地址。

## 结构

```
site/
  index.html              # 机库首页（含 SEO）
  planes/{slug}.html      # 58 个机型详情页（独立 title / meta / JSON-LD）
  styles.css
  app.js / plane.js
  sitemap.xml / robots.txt
  data/planes.json
  assets/planes/{id}/
```


## 说明

- 叠法步骤与示意图整理自 Fold'N Fly，界面与筛选交互为独立实现。
- 仅供个人学习 / 演示；请尊重原站版权，勿用于商业分发。
