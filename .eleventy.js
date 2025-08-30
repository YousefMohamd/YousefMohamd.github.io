const pluginRss = require("@11ty/eleventy-plugin-rss");
const pluginNavigation = require("@11ty/eleventy-navigation");
module.exports = function(eleventyConfig) {
  eleventyConfig.addPlugin(pluginRss);
  eleventyConfig.addPlugin(pluginNavigation);
  eleventyConfig.addPassthroughCopy({ "img": "img" });
  eleventyConfig.addPassthroughCopy({ "css": "css" });
  eleventyConfig.addPassthroughCopy({ "files": "files" });
  eleventyConfig.addFilter("htmlDateString", (d) => new Date(d).toISOString().slice(0, 10));
  eleventyConfig.addFilter("readableDate", (d) =>
    new Date(d).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })
  );
  const EXCLUDED = new Set(["all","nav","post","posts"]);
  eleventyConfig.addFilter("filterTagList", (tags) => (tags || []).filter((t) => !EXCLUDED.has(t)));
  eleventyConfig.addCollection("tagList", (api) => {
    const set = new Set();
    api.getAll().forEach((item) => {
      (item.data.tags || []).forEach((t) => { if(!EXCLUDED.has(t)) set.add(t); });
    });
    return Array.from(set).sort();
  });
  return {
    dir: { input: ".", includes: "_includes", data: "_data", output: "_site" },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
    templateFormats: ["njk","md","html"]
  };
};
