"""电商数据看板页面。

这里故意不引入 React/Vue，而是用一段原生 HTML/CSS/JS。
初学时可以更直观看到：
- 浏览器 fetch 调后端 API
- 后端返回 JSON
- 前端把 JSON 渲染到页面
"""


DASHBOARD_HTML = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>电商数据平台</title>
  <style>
    :root {
      --bg: #f4f6f9;
      --panel: #ffffff;
      --ink: #111827;
      --muted: #667085;
      --line: #d9e0eb;
      --blue: #2563eb;
      --cyan: #0891b2;
      --green: #059669;
      --orange: #d97706;
      --red: #dc2626;
      --slate: #101828;
      --shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", Arial, sans-serif;
      letter-spacing: 0;
    }
    .shell { min-height: 100vh; display: grid; grid-template-columns: 248px 1fr; }
    aside { background: var(--slate); color: #fff; padding: 24px 18px; }
    .brand { display: flex; align-items: center; gap: 12px; margin-bottom: 28px; }
    .brand-mark {
      width: 40px; height: 40px; display: grid; place-items: center;
      border-radius: 9px; background: var(--blue); font-weight: 900;
    }
    .brand strong { display: block; font-size: 17px; }
    .brand span { display: block; margin-top: 2px; color: #98a2b3; font-size: 12px; }
    .nav-title { margin: 24px 8px 10px; color: #98a2b3; font-size: 12px; font-weight: 700; }
    .nav-item {
      width: 100%; height: 40px; display: flex; align-items: center; gap: 10px;
      padding: 0 10px; border: 0; border-radius: 7px; background: transparent;
      color: #d0d5dd; font: inherit; font-size: 14px; text-align: left; cursor: pointer;
    }
    .nav-item:hover { background: #1d2939; color: #fff; }
    .nav-item.active { background: #1d2939; color: #fff; font-weight: 700; }
    .nav-dot { width: 8px; height: 8px; border-radius: 999px; background: #12b76a; }
    .content { min-width: 0; }
    header {
      padding: 24px 32px 16px; background: #fff; border-bottom: 1px solid var(--line);
    }
    .header-row { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; }
    h1 { margin: 0; font-size: 26px; line-height: 1.25; }
    header p { margin: 8px 0 0; color: var(--muted); line-height: 1.6; }
    .system-state {
      display: grid; gap: 6px; min-width: 280px; padding: 12px 14px;
      border: 1px solid var(--line); border-radius: 8px; background: #f8fafc;
      font-size: 13px; color: var(--muted);
    }
    .system-state strong { color: var(--ink); }
    main { width: min(1320px, calc(100vw - 300px)); margin: 22px auto 48px; }
    .toolbar {
      display: grid; grid-template-columns: repeat(5, minmax(120px, 1fr)); gap: 12px;
      padding: 16px; background: var(--panel); border: 1px solid var(--line);
      border-radius: 8px; box-shadow: var(--shadow);
    }
    label { display: grid; gap: 6px; color: var(--muted); font-size: 13px; }
    input, select, .primary-btn {
      height: 40px; border: 1px solid var(--line); border-radius: 6px; padding: 0 12px;
      font: inherit; background: #fff; color: var(--ink);
    }
    input:focus, select:focus { outline: 2px solid rgba(37, 99, 235, 0.16); border-color: var(--blue); }
    .primary-btn {
      margin-top: 19px; background: var(--blue); border-color: var(--blue);
      color: #fff; font-weight: 700; cursor: pointer;
    }
    .primary-btn:hover { background: #1d4ed8; }
    .meta { margin: 14px 0; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; color: var(--muted); font-size: 14px; }
    .badge {
      display: inline-flex; align-items: center; height: 26px; padding: 0 10px;
      border-radius: 999px; background: #e0f2fe; color: #0369a1; font-weight: 700;
    }
    .badge.hit { background: #dcfce7; color: #166534; }
    .badge.miss { background: #fef3c7; color: #92400e; }
    .view { display: none; }
    .view.active { display: block; }
    .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
    .two-col { display: grid; grid-template-columns: 1fr 1.35fr; gap: 14px; margin-top: 14px; }
    .three-col { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
    .card, .panel {
      background: var(--panel); border: 1px solid var(--line); border-radius: 8px; box-shadow: var(--shadow);
    }
    .card { padding: 18px; }
    .card-top { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
    .label { color: var(--muted); font-size: 14px; }
    .metric-icon {
      width: 34px; height: 34px; display: grid; place-items: center; border-radius: 8px;
      background: #eff6ff; color: var(--blue); font-weight: 900;
    }
    .value { margin-top: 12px; font-size: 29px; font-weight: 850; }
    .hint { margin-top: 8px; color: #98a2b3; font-size: 12px; line-height: 1.5; }
    .panel { padding: 18px; min-width: 0; }
    .panel-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
    .panel-head h2 { margin: 0; font-size: 18px; }
    .panel-head span { color: var(--muted); font-size: 13px; }
    .bar-row {
      display: grid; grid-template-columns: minmax(210px, 1.15fr) 1fr 110px;
      gap: 12px; align-items: center; margin: 12px 0;
    }
    .product-name { font-weight: 800; color: #182230; font-size: 15px; line-height: 1.35; }
    .product-meta { margin-top: 3px; color: var(--muted); font-size: 12px; }
    .bar { height: 10px; background: #e5e7eb; border-radius: 999px; overflow: hidden; }
    .bar span { display: block; height: 100%; background: linear-gradient(90deg, var(--blue), var(--cyan)); }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { padding: 10px; border-bottom: 1px solid #edf0f5; text-align: left; vertical-align: top; }
    th { color: var(--muted); font-weight: 700; }
    tbody tr:hover { background: #f8fafc; }
    code, .mono { font-family: Consolas, "Cascadia Mono", monospace; font-size: 12px; }
    .status { font-weight: 800; }
    .paid, .shipped, .hit { color: var(--green); }
    .refunded, .miss { color: var(--orange); }
    .cancelled { color: var(--red); }
    .flow { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-top: 12px; }
    .flow-step {
      min-height: 86px; padding: 12px; border: 1px solid var(--line); border-radius: 8px;
      background: #f8fafc; color: #344054; font-size: 13px; line-height: 1.45;
    }
    .flow-step strong { display: block; color: var(--blue); margin-bottom: 6px; }
    .empty { padding: 26px; color: var(--muted); text-align: center; border: 1px dashed var(--line); border-radius: 8px; }
    .key-cell { max-width: 520px; word-break: break-all; color: #344054; }
    @media (max-width: 1080px) {
      .shell { grid-template-columns: 1fr; }
      aside { display: none; }
      main { width: min(100vw - 24px, 1320px); }
      .header-row, .toolbar, .grid, .two-col, .three-col, .flow { grid-template-columns: 1fr; display: grid; }
      .primary-btn { margin-top: 0; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside>
      <div class="brand">
        <div class="brand-mark">E</div>
        <div><strong>电商数据平台</strong><span>FastAPI Analytics</span></div>
      </div>
      <div class="nav-title">工作台</div>
      <button class="nav-item active" data-view="overview"><span class="nav-dot"></span>经营总览</button>
      <button class="nav-item" data-view="products">商品排行</button>
      <button class="nav-item" data-view="orders">订单监控</button>
      <div class="nav-title">数据链路</div>
      <button class="nav-item" data-view="postgres">PostgreSQL</button>
      <button class="nav-item" data-view="redis">Redis Cache</button>
      <button class="nav-item" data-view="events">API Logs</button>
    </aside>
    <div class="content">
      <header>
        <div class="header-row">
          <div>
            <h1 id="pageTitle">经营数据总览</h1>
            <p id="pageDesc">页面请求 FastAPI，后端聚合 PostgreSQL 订单数据，并将相同筛选条件的结果写入 Redis 缓存。</p>
          </div>
          <div class="system-state">
            <div><strong>服务：</strong>web / postgres / redis</div>
            <div><strong>API：</strong>/api/v1/ecommerce/metrics</div>
            <div><strong>缓存：</strong>Redis TTL 60 秒</div>
          </div>
        </div>
      </header>

      <main>
        <section class="toolbar">
          <label>开始日期 <input id="startDate" type="date" value="2026-01-01"></label>
          <label>结束日期 <input id="endDate" type="date" value="2026-05-26"></label>
          <label>商品品类
            <select id="category">
              <option value="">全部品类</option>
              <option>手机数码</option><option>家居生活</option><option>美妆个护</option>
              <option>运动户外</option><option>食品饮料</option><option>服饰鞋包</option>
            </select>
          </label>
          <label>订单状态
            <select id="status">
              <option value="">全部状态</option>
              <option value="paid">paid 已支付</option><option value="shipped">shipped 已发货</option>
              <option value="refunded">refunded 已退款</option><option value="cancelled">cancelled 已取消</option>
            </select>
          </label>
          <button class="primary-btn" id="refreshBtn">查询数据</button>
        </section>

        <div class="meta">
          <span id="cacheBadge" class="badge">CACHE ...</span>
          <span id="summaryText">正在加载数据</span>
        </div>

        <section id="overview" class="view active">
          <div id="metrics" class="grid"></div>
          <div class="two-col">
            <div class="panel"><div class="panel-head"><h2>热销商品 Top 8</h2><span>按成交额排序</span></div><div id="topProducts"></div></div>
            <div class="panel"><div class="panel-head"><h2>最近订单</h2><span>实时查询结果</span></div><table><thead><tr><th>订单号</th><th>客户</th><th>状态</th><th>渠道</th><th>时间</th><th>金额</th></tr></thead><tbody id="orders"></tbody></table></div>
          </div>
        </section>

        <section id="products" class="view">
          <div class="panel"><div class="panel-head"><h2>商品排行</h2><span>商品名称、品类、销量、成交额</span></div><div id="productRank"></div></div>
        </section>

        <section id="orders-view" class="view">
          <div class="panel"><div class="panel-head"><h2>订单监控</h2><span>最近 12 条订单</span></div><table><thead><tr><th>订单号</th><th>客户</th><th>状态</th><th>渠道</th><th>时间</th><th>金额</th></tr></thead><tbody id="ordersFull"></tbody></table></div>
        </section>

        <section id="postgres" class="view">
          <div class="three-col" id="dbTables"></div>
          <div class="two-col">
            <div class="panel"><div class="panel-head"><h2>订单状态分布</h2><span>来自 PostgreSQL group by</span></div><div id="statusDist"></div></div>
            <div class="panel"><div class="panel-head"><h2>品类成交额</h2><span>来自 PostgreSQL 聚合查询</span></div><div id="categoryRevenue"></div></div>
          </div>
        </section>

        <section id="redis" class="view">
          <div class="grid" id="redisCards"></div>
          <div class="panel" style="margin-top:14px"><div class="panel-head"><h2>Redis 查询流程</h2><span>看懂缓存命中</span></div><div id="redisFlow" class="flow"></div></div>
          <div class="panel" style="margin-top:14px"><div class="panel-head"><h2>缓存 Key 与 TTL</h2><span>同样筛选条件会复用 key</span></div><table><thead><tr><th>Key</th><th>TTL</th><th>大小</th><th>值预览</th></tr></thead><tbody id="redisKeys"></tbody></table></div>
        </section>

        <section id="events" class="view">
          <div class="panel"><div class="panel-head"><h2>最近 API 查询事件</h2><span>观察 MISS -> HIT</span></div><table><thead><tr><th>时间</th><th>缓存</th><th>数据来源</th><th>耗时</th><th>Key</th></tr></thead><tbody id="eventRows"></tbody></table></div>
        </section>
      </main>
    </div>
  </div>

  <script>
    const $ = (id) => document.getElementById(id);
    const money = (value) => `¥${Number(value).toLocaleString("zh-CN", { maximumFractionDigits: 2 })}`;
    const icons = ["¥", "#", "人", "均"];
    let dashboardData = null;

    const titles = {
      overview: ["经营数据总览", "页面请求 FastAPI，后端聚合 PostgreSQL 订单数据，并将相同筛选条件的结果写入 Redis 缓存。"],
      products: ["商品排行", "从 PostgreSQL 聚合商品销量和成交额，字体和布局更适合阅读商品名称。"],
      orders: ["订单监控", "查看最近订单，理解业务明细如何从订单表和明细表关联查询。"],
      postgres: ["PostgreSQL 数据库", "可视化表数据量、订单状态分布和品类成交额。"],
      redis: ["Redis Cache", "观察缓存 key、TTL、内存占用，以及查询如何从 MISS 变成 HIT。"],
      events: ["API Logs", "记录最近查询事件，展示 Redis 命中、PostgreSQL 回源和耗时。"],
    };

    function buildQuery() {
      const params = new URLSearchParams();
      for (const key of ["startDate", "endDate", "category", "status"]) {
        const value = $(key).value;
        const apiKey = key === "startDate" ? "start_date" : key === "endDate" ? "end_date" : key;
        if (value) params.set(apiKey, value);
      }
      return params.toString();
    }

    function setView(view) {
      document.querySelectorAll(".nav-item").forEach(btn => btn.classList.toggle("active", btn.dataset.view === view));
      document.querySelectorAll(".view").forEach(el => el.classList.remove("active"));
      const target = view === "orders" ? "orders-view" : view;
      $(target).classList.add("active");
      $("pageTitle").textContent = titles[view][0];
      $("pageDesc").textContent = titles[view][1];
      if (view === "postgres") loadDatabase();
      if (view === "redis") loadRedis();
      if (view === "events") loadEvents();
    }

    function renderMetrics(metrics) {
      $("metrics").innerHTML = metrics.map((item, index) => `
        <article class="card"><div class="card-top"><div class="label">${item.title}</div><div class="metric-icon">${icons[index] || "•"}</div></div>
        <div class="value">${item.suffix === "¥" ? money(item.value) : Number(item.value).toLocaleString("zh-CN") + item.suffix}</div>
        <div class="hint">当前筛选条件下的聚合结果</div></article>
      `).join("");
    }

    function productRows(products, full=false) {
      if (!products.length) return `<div class="empty">当前筛选条件下暂无商品数据</div>`;
      const max = Math.max(...products.map(p => p.revenue), 1);
      return products.map((p, i) => `
        <div class="bar-row">
          <div><div class="product-name">${full ? `${i + 1}. ` : ""}${p.name}</div><div class="product-meta">${p.category} · ${p.quantity} 件</div></div>
          <div class="bar"><span style="width:${Math.round(p.revenue / max * 100)}%"></span></div>
          <div class="mono">${money(p.revenue)}</div>
        </div>
      `).join("");
    }

    function orderRows(orders) {
      if (!orders.length) return `<tr><td colspan="6"><div class="empty">当前筛选条件下暂无订单</div></td></tr>`;
      return orders.map(o => `<tr><td class="mono">${o.order_no}</td><td>${o.customer}</td><td class="status ${o.status}">${o.status}</td><td>${o.channel}</td><td>${o.ordered_at}</td><td class="mono">${money(o.amount)}</td></tr>`).join("");
    }

    function renderDashboard(data) {
      dashboardData = data;
      $("cacheBadge").textContent = `CACHE ${data.cache}`;
      $("cacheBadge").className = `badge ${data.cache.toLowerCase()}`;
      $("summaryText").textContent = data.cache === "HIT"
        ? `本次结果来自 Redis 缓存，耗时 ${data.elapsed_ms}ms`
        : `本次结果来自 PostgreSQL，并写入 Redis，耗时 ${data.elapsed_ms}ms`;
      renderMetrics(data.metrics);
      $("topProducts").innerHTML = productRows(data.top_products);
      $("productRank").innerHTML = productRows(data.top_products, true);
      $("orders").innerHTML = orderRows(data.recent_orders);
      $("ordersFull").innerHTML = orderRows(data.recent_orders);
    }

    async function loadDashboard() {
      $("summaryText").textContent = "正在查询 PostgreSQL / Redis ...";
      const response = await fetch(`/api/v1/ecommerce/metrics?${buildQuery()}`);
      renderDashboard(await response.json());
      loadEvents();
    }

    async function loadDatabase() {
      const data = await (await fetch("/api/v1/ecommerce/database")).json();
      $("dbTables").innerHTML = data.tables.map(t => `<article class="card"><div class="label">${t.description}</div><div class="value">${t.rows.toLocaleString("zh-CN")}</div><div class="hint mono">${t.name}</div></article>`).join("");
      const maxStatus = Math.max(...data.status_distribution.map(x => x.count), 1);
      $("statusDist").innerHTML = data.status_distribution.map(x => `<div class="bar-row"><div><strong>${x.status}</strong></div><div class="bar"><span style="width:${Math.round(x.count / maxStatus * 100)}%"></span></div><div>${x.count}</div></div>`).join("");
      const maxRevenue = Math.max(...data.category_revenue.map(x => x.revenue), 1);
      $("categoryRevenue").innerHTML = data.category_revenue.map(x => `<div class="bar-row"><div><strong>${x.category}</strong><div class="product-meta">${x.products} 个商品</div></div><div class="bar"><span style="width:${Math.round(x.revenue / maxRevenue * 100)}%"></span></div><div>${money(x.revenue)}</div></div>`).join("");
    }

    async function loadRedis() {
      const data = await (await fetch("/api/v1/ecommerce/redis")).json();
      $("redisCards").innerHTML = `
        <article class="card"><div class="label">缓存 Key 数</div><div class="value">${data.key_count}</div><div class="hint">匹配 ecommerce:dashboard:*</div></article>
        <article class="card"><div class="label">当前内存</div><div class="value">${data.memory.used_memory_human || "-"}</div><div class="hint">Redis used_memory_human</div></article>
        <article class="card"><div class="label">峰值内存</div><div class="value">${data.memory.used_memory_peak_human || "-"}</div><div class="hint">Redis used_memory_peak_human</div></article>
        <article class="card"><div class="label">缓存 TTL</div><div class="value">60s</div><div class="hint">过期后会重新查 PostgreSQL</div></article>`;
      $("redisFlow").innerHTML = data.flow.map((text, i) => `<div class="flow-step"><strong>${i + 1}</strong>${text}</div>`).join("");
      $("redisKeys").innerHTML = data.keys.length ? data.keys.map(k => `<tr><td class="key-cell mono">${k.key}</td><td>${k.ttl}s</td><td>${k.bytes} B</td><td class="key-cell mono">${k.preview}</td></tr>`).join("") : `<tr><td colspan="4"><div class="empty">暂无缓存 key。先点击“查询数据”生成一次 MISS。</div></td></tr>`;
    }

    async function loadEvents() {
      const data = await (await fetch("/api/v1/ecommerce/events")).json();
      $("eventRows").innerHTML = data.events.length ? data.events.map(e => `<tr><td>${e.time}</td><td class="${e.cache.toLowerCase()}"><strong>${e.cache}</strong></td><td>${e.source}</td><td>${e.elapsed_ms}ms</td><td class="key-cell mono">${e.cache_key}</td></tr>`).join("") : `<tr><td colspan="5"><div class="empty">暂无事件。先执行一次查询。</div></td></tr>`;
    }

    document.querySelectorAll(".nav-item").forEach(btn => btn.addEventListener("click", () => setView(btn.dataset.view)));
    $("refreshBtn").addEventListener("click", loadDashboard);
    loadDashboard();
  </script>
</body>
</html>
"""
