const pluginRss = require("@11ty/eleventy-plugin-rss");

module.exports = function (eleventyConfig) {
  // Static passthrough
  eleventyConfig.addPassthroughCopy("css");
  eleventyConfig.addPassthroughCopy("js");
  eleventyConfig.addPassthroughCopy("img");
  eleventyConfig.addPassthroughCopy("files");

  // Watch targets
  eleventyConfig.addWatchTarget("css");
  eleventyConfig.addWatchTarget("js");
  eleventyConfig.addWatchTarget("img/showreel");

  // RSS plugin + filters
  eleventyConfig.addPlugin(pluginRss);

  eleventyConfig.addFilter("absoluteUrl", (url, base) =>
    pluginRss.absoluteUrl(url, base)
  );

  eleventyConfig.addFilter("htmlDateString", (dateObj) => {
    try {
      return new Date(dateObj).toISOString();
    } catch {
      return "";
    }
  });

  eleventyConfig.addFilter("readableDate", (dateObj) => {
    try {
      const d = new Date(dateObj);
      return new Intl.DateTimeFormat("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      }).format(d);
    } catch {
      return "";
    }
  });

  // tagList collection
  eleventyConfig.addCollection("tagList", (collectionsApi) => {
    const set = new Set();
    collectionsApi.getAll().forEach((item) => {
      (item.data.tags || []).forEach((t) => set.add(t));
    });
    return [...set];
  });

  // Eleventy config
  return {
    dir: { input: ".", includes: "_includes", data: "_data", output: "_site" },
    serverOptions: { liveReload: false, domDiff: false, port: 8087 },
  };
};
