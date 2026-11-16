(() => {
  const STORAGE_KEY = "ppw-lang";

  const STRINGS = {
    zh: {
      brandTitle: "纸飞机机库",
      brandSub: "Folding Hangar",
      navHangar: "机库",
      navLearn: "学折",
      nav3dLearn: "3D 学折",
      l3dTitle: "机库目录",
      l3dLead: "站内全部 58 款纸飞机。点选机型旋转 3D 模型，准备好了再打开图解折法。",
      l3dStageKicker: "3D 预览",
      l3dLabCta: "打开 3D 试飞室",
      navRead: "阅读实验",
      navGuides: "指南",
      guidesMeta: "工坊",
      guidesTitle: "飞行工坊",
      guidesLead: "人们常问 ChatGPT 和搜索引擎的纸飞机问题——用短、可引用的指南回答，可与机库对照阅读。",
      guidesTldrTitle: "直接答案",
      guidesFaqTitle: "最常被问到的问题",
      guidesFaqLead: "先给短答——需要步骤时再打开完整指南。",
      navVideo: "视频教程",
      navFly: "试飞",
      vgKicker: "分步折法教程",
      vgTitle: "折出厉害的纸飞机。",
      vgLead: "按难度与机型筛选，对比速度、滑翔与精准度，再打开完整图解折法——58 款随时开折。",
      vgCtaFold: "浏览教程",
      vgCtaFly: "试试 3D 试飞",
      vgDiffLegend: "折叠难度",
      vgTypeLegend: "机型类型",
      vgPaperLegend: "纸张规格",
      vgTypeDart: "飞镖",
      vgTypeGlider: "滑翔",
      vgTypeHybrid: "混合",
      vgTypeJet: "喷气造型",
      vgTypeStunt: "特技",
      vgRecommended: "推荐机型",
      vgRecommendedLead: "不妨先从这几架开始。",
      vgListTitle: "点任意一架开始折",
      vgMatch: "款教程符合筛选。",
      vgCount: "{n} / {total} 教程",
      vgStatSpeed: "速度",
      vgStatGlide: "滑翔",
      vgStatAccuracy: "精准",
      readMetaShort: "约 3 分钟",
      readTocTitle: "本页目录",
      learnTitle: "机库目录",
      learnLead: "站内全部 58 款纸飞机，每架都有完整图解。按难度分组，方便从入门一路练到专家机型。",
      learnFilterAria: "筛选机型",
      learnFilterBeginner: "入门",
      learnFilterGliders: "停得久",
      learnFilterDistance: "飞得远",
      learnFilterStunts: "玩特技",
      learnFilterDecorative: "好看摆设",
      learnFilterScissors: "需要剪",
      learnCount: "{n} / {total} 架",
      learnFilterStatus: "当前筛选显示 {n} / {total} 架",
      workshopTitle: "工坊",
      workshopLead: "选纸、排障、挑机型、公平试飞，以及背后的飞行原理。",
      wsFixKicker: "飞行工坊",
      wsFixTitle: "纸飞机为什么会栽头、失速或转弯",
      wsFixSum: "先给飞行模式命名，再做一个对应的小调整。",
      wsPaperKicker: "动手之前",
      wsPaperTitle: "影响纸飞机飞行的因素",
      wsPaperSum: "纸张克重、左右对称、重心、投掷角度与空气——几乎能解释所有“意外飞行”。",
      wsChooseKicker: "挑选机型",
      wsChooseTitle: "按飞行目标选一架",
      wsChooseSum: "从入门飞镖、挑战远距，到延长滞空，三条短路径进入机库。",
      wsFlyKicker: "做个实验",
      wsReadTitle: "怎样公平地测试纸飞机飞行",
      wsReadSum: "一把卷尺、一条起飞线、十次投掷——一次只改一件事，交替投 A/B，用中位数计分。",
      wsSimKicker: "3D 实验室",
      wsFlyTitle: "折之前先试飞 3D 模型",
      wsFlySum: "旋转任意机型，调节发射角度，对比估算距离与滞空时间。",
      flyKicker: "3D 飞行实验室",
      flyTitle: "先试飞，再动手折",
      flyLead: "选择任意一款纸飞机，拖动查看 3D 模型，调整发射角度后直接试飞，看看它能飞多远、能停在空中多久。",
      pickTitle: "1 · 选择纸飞机",
      pickLead: "58 款机型任选其一，右侧的 3D 模型与试飞数据会同步更新。",
      dragHint: "拖动模型可旋转视角",
      viewerStats: "估算距离",
      viewerTime: "估算滞空",
      viewerGuide: "查看折法",
      testTitle: "2 · 试飞",
      testLead: "调节发射角度后点击“发射”，观察滑翔轨迹与落点。",
      launchAngle: "发射角度",
      launchBtn: "发射",
      liveDistance: "飞行距离",
      liveTime: "滞空时间",
      landed: "已落地",
      flyIntroTitle: "这个页面能做什么",
      flyIntro1: "3D 模型按每一款机型的真实比例绘制：拖动可以旋转视角，从侧面、顶部和正面检查机翼与机头的形状。",
      flyIntro2: "试飞会依据该机型的估算航程与滞空数据模拟滑翔轨迹，你可以反复调整发射角度，找到最合适的投掷方式。",
      flyIntro3: "落地之后，回到折法页面照着步骤折一架，再和模拟结果对比，就能判断折痕与对称是否做到位。",
      loading: "加载中…",
      loadFail: "加载失败",
      kicker: "逐步图解 · 打开就能折",
      heroTitle: "纸飞机折法图解",
      heroLead: "58 种经典纸飞机折法，按飞行目标与难度筛选，每一步都有图解。",
      catalogTitle: "全部纸飞机",
      catalogLead: "按你想怎么飞来挑：飞得远、停得久、玩特技，或折一架好看的摆设。",
      browse: "浏览机型",
      shuffle: "随机一架",
      search: "搜索机型…",
      sort: "排序",
      sortPopularity: "人气",
      sortName: "名称",
      sortDifficulty: "折纸难度",
      sortDistance: "飞得远",
      sortTime: "停得久",
      type: "想飞成什么样",
      goalHint: "不勾选则显示全部机型。",
      tagDistance: "飞得远",
      tagTime: "停得久",
      tagAcrobatic: "玩特技",
      tagDecorative: "好看摆设",
      difficulty: "折纸难度",
      diffEasy: "入门",
      diffMedium: "进阶",
      diffHard: "挑战",
      diffExpert: "大师",
      scissors: "动手准备",
      cutAny: "不限",
      cutNo: "只用手折",
      cutYes: "需要剪一刀",
      empty: "没有匹配的机型，试试放宽筛选。",
      footer: "纸飞机机库 · 纯静态叠法图解",
      count: "{n} / {total} 架",
      needScissors: "需剪",
      noScissors: "只用手折",
      needScissorsLong: "需要剪一刀",
      back: "← 返回机库",
      stepsTitle: "叠法步骤",
      stepLabel: "步骤 {n}",
      stepsCount: "{n} 步",
      perfTitle: "飞行参考",
      perfType: "最适合",
      perfDistance: "估算飞行距离",
      perfTime: "估算滞空时间",
      perfDifficulty: "折纸难度",
      perfPaper: "用纸与步数",
      perfThrow: "投掷方式",
      perfNote: "以上估算基于无风天气、水平投掷与调整良好的纸飞机。",
      faqTitle: "常见问题",
      filterAria: "筛选",
      planeAlt: "{name} 纸飞机",
      recommendTitle: "按目标选机型",
      recommendLead: "不确定从哪一架开始？先按你的飞行目标挑选。",
      recBeginnerLabel: "新手入门",
      recDistanceLabel: "挑战远距",
      recTimeLabel: "延长滞空",
      recBeginnerText: "折法经典、步骤清楚，第一次折也能轻松跟上。",
      recDistanceText: "适合练习高速直线飞行，可以尝试不同投掷角度。",
      recTimeText: "轻投即可滑翔，适合观察机翼调整对滞空的影响。",
      recCta: "查看折法 →",
      guideTitle: "折叠指南与常见问题",
      guideLead: "从选纸、压折痕到试飞微调，掌握这些细节会更容易折出稳定的纸飞机。",
      featuresTitle: "3D 折法教程与试飞",
      featuresLead: "每款机型都配有分步图解、飞行估算，以及完成后的滑翔预览。",
      feat3dTitle: "3D 逐步图解教程",
      feat3dText: "每一步都能从侧面、顶部和正面查看，机翼角度与机头对齐一眼看清，照着折更不容易出错。",
      featFlyTitle: "试飞预览与飞行数据",
      featFlyText: "查看每架飞机的估算距离与滞空时间，并预览它的滑翔轨迹，再把自己的飞机调整到接近的状态。",
      featFilterTitle: "58 款机型，按目标挑",
      featFilterText: "先选你想怎么飞，再按折纸难度和是否需要剪刀收窄，也能按人气、距离或滞空排序。",
      factorsTitle: "影响纸飞机飞行的因素",
      factorsLead: "同一张纸折出的两架飞机，表现可能完全不同。下面五个细节几乎能解释所有“意外飞行”。",
      factorPaperTitle: "纸张克重",
      factorPaperText: "轻纸滑翔慢、滞空久；重纸飞得快但更容易失速。70–80g 的打印纸适合大多数机型。",
      factorSymTitle: "左右对称",
      factorSymText: "只要一侧机翼宽出一毫米或角度不同，飞机就会转向。每折完一步都从正面检查两翼。",
      factorCgTitle: "重心位置",
      factorCgText: "重心太靠前会栽头，太靠后则容易失速或翻跟头。可通过调整机翼后缘或机尾来平衡。",
      factorLaunchTitle: "投掷角度与力度",
      factorLaunchText: "远距机型适合有力、水平的投掷；滑翔机型则需要轻放，并让机头略向上扬。",
      factorAirTitle: "空气与环境",
      factorAirText: "室内气流稳定、结果可复现；户外有风会带来额外升力与乱流。先在室内试飞，再拿到户外。",
    },
    en: {
      brandTitle: "Paper Airplane",
      brandSub: "Folding Hangar",
      navHangar: "Hangar",
      navLearn: "Learn",
      nav3dLearn: "3D Learn",
      l3dTitle: "The hangar",
      l3dLead: "Every plane on the site, 58 in all. Pick one to spin the 3D model, then open the folds when you are ready.",
      l3dStageKicker: "3D preview",
      l3dLabCta: "Open 3D flight lab",
      navRead: "Read & Learn",
      navGuides: "Guides",
      guidesMeta: "Workshop",
      guidesTitle: "Flight workshop",
      guidesLead: "The questions people ask ChatGPT and search engines about paper airplanes — answered in short, citable guides you can open beside the hangar.",
      guidesTldrTitle: "Direct answers",
      guidesFaqTitle: "Questions people ask most",
      guidesFaqLead: "Short answers first — open a full guide when you need the steps.",
      navVideo: "Video Guide",
      navFly: "Fly",
      vgKicker: "Step-by-step folding guides",
      vgTitle: "Fold epic paper airplanes.",
      vgLead: "Filter the hangar by difficulty and plane type, compare speed, glide and accuracy, then open a full diagrammed guide — 58 designs ready to fold.",
      vgCtaFold: "Browse guides",
      vgCtaFly: "Try 3D flight",
      vgDiffLegend: "Folding difficulty",
      vgTypeLegend: "Plane type",
      vgPaperLegend: "Paper type",
      vgTypeDart: "Dart",
      vgTypeGlider: "Glider",
      vgTypeHybrid: "Hybrid",
      vgTypeJet: "Jet",
      vgTypeStunt: "Stunt",
      vgRecommended: "Recommended planes",
      vgRecommendedLead: "Try one of these first.",
      vgListTitle: "Click any plane to fold it",
      vgMatch: "guides match your search.",
      vgCount: "{n} / {total} guides",
      vgStatSpeed: "Speed",
      vgStatGlide: "Glide",
      vgStatAccuracy: "Accuracy",
      readMetaShort: "3 min read",
      readTocTitle: "On this page",
      learnTitle: "The hangar",
      learnLead: "Every plane on the site, 58 in all, each with a full diagrammed guide. They are grouped by difficulty, because that is where the learning path really differs.",
      learnFilterAria: "Show planes",
      learnFilterBeginner: "Beginner",
      learnFilterGliders: "Long floats",
      learnFilterDistance: "Far throws",
      learnFilterStunts: "Tricks",
      learnFilterDecorative: "Display",
      learnFilterScissors: "Needs a cut",
      learnCount: "{n} / {total} planes",
      learnFilterStatus: "Showing {n} of {total} planes",
      workshopTitle: "Workshop",
      workshopLead: "Materials, troubleshooting, choosing a design, fair tests and the physics underneath.",
      wsFixKicker: "Flight workshop",
      wsFixTitle: "Why your paper airplane dives, stalls, or turns",
      wsFixSum: "Name the flight pattern first, then make the one small change that matches it.",
      wsPaperKicker: "Before you fold",
      wsPaperTitle: "What changes how a paper airplane flies",
      wsPaperSum: "Paper weight, symmetry, centre of gravity, launch angle, and air — the five details behind almost every surprise flight.",
      wsChooseKicker: "Choose a design",
      wsChooseTitle: "Pick a plane by flying goal",
      wsChooseSum: "Start with a beginner dart, chase distance, or stretch hang time — three short paths into the hangar.",
      wsFlyKicker: "Try an experiment",
      wsReadTitle: "How to run a fair paper airplane flight test",
      wsReadSum: "A tape measure, a starting line and ten throws — change one thing, alternate A and B, score with the median.",
      wsSimKicker: "3D lab",
      wsFlyTitle: "Test-fly a 3D model before you fold",
      wsFlySum: "Rotate any design, set a launch angle, and compare estimated distance and hang time.",
      flyKicker: "3D flight lab",
      flyTitle: "Fly it before you fold it",
      flyLead: "Pick any paper airplane, drag to inspect its 3D model, then set a launch angle and test-fly it to see how far and how long it can glide.",
      pickTitle: "1 · Choose a paper airplane",
      pickLead: "Pick one of 58 designs; the 3D model and flight data update instantly.",
      dragHint: "Drag the model to rotate the view",
      viewerStats: "Estimated distance",
      viewerTime: "Estimated hang time",
      viewerGuide: "Open folding guide",
      testTitle: "2 · Test flight",
      testLead: "Set a launch angle, press launch, and watch the glide path and landing spot.",
      launchAngle: "Launch angle",
      launchBtn: "Launch",
      liveDistance: "Distance",
      liveTime: "Hang time",
      landed: "Landed",
      flyIntroTitle: "What this page does",
      flyIntro1: "Each 3D model is drawn to the proportions of its design. Drag to rotate and check the wings and nose from the side, top, and front.",
      flyIntro2: "The test flight simulates a glide using that plane's estimated range and hang time, so you can try different launch angles and find the best throw.",
      flyIntro3: "Once it lands, open the folding guide, fold your own, and compare it with the simulation to see whether your creases and symmetry match.",
      loading: "Loading…",
      loadFail: "Failed to load",
      kicker: "Step-by-step · Fold and fly",
      heroTitle: "Paper Airplane Folding Guides",
      heroLead: "58 classic paper airplanes with 3D step-by-step folds, flight estimates, and a test-flight preview.",
      catalogTitle: "All paper airplanes",
      catalogLead: "Pick by how you want it to fly: far throws, long floats, tricks, or a display piece.",
      browse: "Browse planes",
      shuffle: "Random plane",
      search: "Search planes…",
      sort: "Sort",
      sortPopularity: "Popularity",
      sortName: "Name",
      sortDifficulty: "Folding skill",
      sortDistance: "Far throws",
      sortTime: "Long floats",
      type: "Best for",
      goalHint: "Leave empty to see every plane.",
      tagDistance: "Far throws",
      tagTime: "Long floats",
      tagAcrobatic: "Tricks",
      tagDecorative: "Display",
      difficulty: "Folding skill",
      diffEasy: "Beginner",
      diffMedium: "Intermediate",
      diffHard: "Advanced",
      diffExpert: "Master",
      scissors: "Fold prep",
      cutAny: "Any prep",
      cutNo: "Hands only",
      cutYes: "Needs a cut",
      empty: "No planes match. Try widening your filters.",
      footer: "Paper Planes World · Static folding guides",
      count: "{n} / {total} planes",
      needScissors: "Needs cut",
      noScissors: "Hands only",
      needScissorsLong: "Needs a cut",
      back: "← Back to hangar",
      stepsTitle: "Folding steps",
      stepLabel: "Step {n}",
      stepsCount: "{n} steps",
      perfTitle: "Flight notes",
      perfType: "Best for",
      perfDistance: "Estimated distance",
      perfTime: "Estimated hang time",
      perfDifficulty: "Folding skill",
      perfPaper: "Paper & folds",
      perfThrow: "How to throw",
      perfNote: "Estimates assume a calm day, a level launch, and a well-trimmed plane.",
      faqTitle: "Frequently asked questions",
      filterAria: "Filters",
      planeAlt: "{name} paper airplane",
      recommendTitle: "Choose by flying goal",
      recommendLead: "Not sure where to start? Pick a plane based on how you want it to fly.",
      recBeginnerLabel: "Start here",
      recDistanceLabel: "Fly farther",
      recTimeLabel: "Stay aloft longer",
      recBeginnerText: "An iconic design with clear steps that makes a great first fold.",
      recDistanceText: "Built for fast, straight flights and experimenting with different launch angles.",
      recTimeText: "Glides with a gentle toss, making it useful for testing wing adjustments and hang time.",
      recCta: "View folding guide →",
      guideTitle: "Folding tips and common questions",
      guideLead: "From choosing paper to sharpening creases and trimming your plane, these details help create steadier flights.",
      featuresTitle: "3D folding guides and test flights",
      featuresLead: "Every design comes with step-by-step folds, flight estimates, and a preview of how it should glide.",
      feat3dTitle: "3D step-by-step tutorials",
      feat3dText: "Check every crease from the side, top, and front before moving on, so wing angles and nose alignment are easy to copy.",
      featFlyTitle: "Test flights and flight data",
      featFlyText: "See the estimated distance and hang time for each plane, plus a preview of its glide path, then trim your own to match.",
      featFilterTitle: "58 planes, pick by goal",
      featFilterText: "Start with how you want it to fly, then narrow by folding skill and whether you need scissors — or sort by popularity, distance, or hang time.",
      factorsTitle: "What changes how a paper airplane flies",
      factorsLead: "Two planes folded from the same sheet can behave completely differently. These five details explain almost every surprise flight.",
      factorPaperTitle: "Paper weight",
      factorPaperText: "Light paper glides slowly and stays aloft; heavy paper flies fast but stalls sooner. 70–80 gsm printer paper suits most designs.",
      factorSymTitle: "Left–right symmetry",
      factorSymText: "If one wing is a millimetre wider or angled differently, the plane turns. Check both wings from the front after every fold.",
      factorCgTitle: "Centre of gravity",
      factorCgText: "Too far forward and the nose dives; too far back and the plane stalls or loops. Shift the balance with trailing-edge or tail adjustments.",
      factorLaunchTitle: "Launch angle and speed",
      factorLaunchText: "Distance designs prefer a firm, level throw. Gliders need a gentle release with the nose slightly up.",
      factorAirTitle: "Air and space",
      factorAirText: "Indoor air is still and predictable, while outdoor wind adds lift and turbulence. Test inside first, then move outside.",
    },
  };

  const DIFF = {
    zh: { Easy: "入门", Medium: "进阶", Hard: "挑战", Expert: "大师" },
    en: {
      Easy: "Beginner",
      Medium: "Intermediate",
      Hard: "Advanced",
      Expert: "Master",
    },
  };

  const TAG = {
    zh: {
      distance: "飞得远",
      time_aloft: "停得久",
      acrobatic: "玩特技",
      decorative: "好看摆设",
    },
    en: {
      distance: "Far throws",
      time_aloft: "Long floats",
      acrobatic: "Tricks",
      decorative: "Display",
    },
  };

  function detect() {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved === "zh" ? "zh" : "en";
  }

  function t(key, vars = {}) {
    const lang = window.PPW.lang;
    let s = STRINGS[lang][key] ?? STRINGS.en[key] ?? key;
    Object.entries(vars).forEach(([k, v]) => {
      s = s.replaceAll(`{${k}}`, String(v));
    });
    return s;
  }

  function ensureSwitcher() {
    let wrap = document.querySelector(".lang-switch");
    if (wrap) return wrap;
    const meta = document.querySelector(".topbar-meta");
    if (!meta) return null;
    wrap = document.createElement("div");
    wrap.className = "lang-switch";
    wrap.innerHTML = `
      <select class="lang-select" aria-label="Language">
        <option value="en">English</option>
        <option value="zh">中文</option>
      </select>
    `;
    meta.prepend(wrap);
    wrap.querySelector(".lang-select").addEventListener("change", (e) => {
      setLang(e.target.value);
    });
    return wrap;
  }

  function applyI18nTextNodes() {
    document.querySelectorAll(".i18n-text[data-zh]").forEach((el) => {
      if (!el.dataset.en) el.dataset.en = el.textContent;
      el.textContent =
        window.PPW.lang === "zh" ? el.dataset.zh : el.dataset.en;
    });
  }

  function applyStatic() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (!key) return;
      const attr = el.getAttribute("data-i18n-attr");
      const value = t(key);
      if (attr) el.setAttribute(attr, value);
      else el.textContent = value;
    });

    document.querySelectorAll("[data-i18n-html]").forEach((el) => {
      el.innerHTML = t(el.getAttribute("data-i18n-html"));
    });

    document.documentElement.lang = window.PPW.lang === "zh" ? "zh-CN" : "en";
    document.documentElement.dataset.lang = window.PPW.lang;

    const select = document.querySelector(".lang-select");
    if (select) select.value = window.PPW.lang;

    // Legacy dual nodes (guide pages): hide the inactive language.
    document.querySelectorAll(".lang-zh, .lang-en").forEach((el) => {
      const show =
        (el.classList.contains("lang-zh") && window.PPW.lang === "zh") ||
        (el.classList.contains("lang-en") && window.PPW.lang === "en");
      el.hidden = !show;
    });

    applyI18nTextNodes();
  }

  function setLang(lang) {
    if (lang !== "zh" && lang !== "en") return;
    window.PPW.lang = lang;
    localStorage.setItem(STORAGE_KEY, lang);
    ensureSwitcher();
    applyStatic();
    window.dispatchEvent(new CustomEvent("ppw:lang", { detail: { lang } }));
  }

  window.PPW = {
    lang: detect(),
    t,
    setLang,
    applyStatic,
    tagLabel: (tag) => TAG[window.PPW.lang][tag] || tag,
    diffLabel: (d) => DIFF[window.PPW.lang][d] || d,
  };

  ensureSwitcher();
  applyStatic();
})();
