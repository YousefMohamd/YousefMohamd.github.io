const pluginRss = require("@11ty/eleventy-plugin-rss");

module.exports = function(eleventyConfig) {
  /* ==== Static passthrough (لازم) ==== */
  eleventyConfig.addPassthroughCopy({ "css": "css" });
  eleventyConfig.addPassthroughCopy({ "js": "js" });
  eleventyConfig.addPassthroughCopy({ "img": "img" });
  eleventyConfig.addPassthroughCopy({ "files": "files" }); // لو موجود

  /* ==== Watch targets ==== */
  eleventyConfig.addWatchTarget("css");
  eleventyConfig.addWatchTarget("js");
  eleventyConfig.addWatchTarget("img/showreel");

  /* ==== RSS filters & fixes (علاج absoluteUrl/htmlDate/readableDate) ==== */
  eleventyConfig.addPlugin(pluginRss);
  eleventyConfig.addFilter("absoluteUrl", (url, base) => pluginRss.absoluteUrl(url, base));
  eleventyConfig.addFilter("htmlDateString", (dateObj) => {
    try { return new Date(dateObj).toISOString(); } catch { return ""; }
  });
  eleventyConfig.addFilter("readableDate", (dateObj) => {
    try {
      const d = new Date(dateObj);
      return new Intl.DateTimeFormat("en-GB", { day:"2-digit", month:"short", year:"numeric" }).format(d);
    } catch { return ""; }
  });

  /* ==== tagList collection (عشان tags.njk ما يهنّش) ==== */
  eleventyConfig.addCollection("tagList", (collectionsApi) => {
    const set = new Set();
    collectionsApi.getAll().forEach(item => (item.data.tags || []).forEach(t => set.add(t)));
    return [...set];
  });

  /* ==== Server options (نقفل liveReload اللي كان عامل RSV1) ==== */
  return {
    dir: { input: ".", includes: "_includes", data: "_data", output: "_site" },
    serverOptions: { liveReload: false, domDiff: false, port: 8087 }
  };
};
