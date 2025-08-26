// .eleventy.js
const pluginRss = require("@11ty/eleventy-plugin-rss");

module.exports = function(eleventyConfig) {
  // Plugins
  eleventyConfig.addPlugin(pluginRss);

  // Static passthrough
  eleventyConfig.addPassthroughCopy({ "img": "img" });
  eleventyConfig.addPassthroughCopy({ "css": "css" });
  eleventyConfig.addPassthroughCopy({ "files": "files" });

  // ---- Dates (fallbacks للـ قوالب) ----
  eleventyConfig.addFilter("htmlDateString", (dateObj) => {
    const d = new Date(dateObj);
    return d.toISOString().slice(0, 10); // YYYY-MM-DD لـ <time datetime="">
  });
  eleventyConfig.addFilter("readableDate", (dateObj) => {
    const d = new Date(dateObj);
    return d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
  });

  // ---- Tags utilities (زي تمبلت Eleventy Base Blog) ----
  const EXCLUDED = new Set(["all", "nav", "post", "posts"]);
  eleventyConfig.addFilter("filterTagList", (tags) =>
    (tags || []).filter((t) => !EXCLUDED.has(t))
  );
  eleventyConfig.addCollection("tagList", (collectionApi) => {
    const tagSet = new Set();
    collectionApi.getAll().forEach((item) => {
      (item.data.tags || []).forEach((tag) => {
        if (!EXCLUDED.has(tag)) tagSet.add(tag);
      });
    });
    return Array.from(tagSet).sort();
  });

  return {
    dir: { input: ".", includes: "_includes", data: "_data", output: "_site" },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
    templateFormats: ["njk","md","html"]
  };
};
