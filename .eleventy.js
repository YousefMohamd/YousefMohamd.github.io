const pluginRss = require("@11ty/eleventy-plugin-rss");
const htmlmin = require("html-minifier-terser");

module.exports = function (eleventyConfig) {
  // Static passthrough
  eleventyConfig.addPassthroughCopy("css");
  eleventyConfig.addPassthroughCopy("js");
  eleventyConfig.addPassthroughCopy("img");
  eleventyConfig.addPassthroughCopy("files");
  eleventyConfig.addPassthroughCopy("fonts"); // Added fonts directory

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

  // HTML Minifier Transform (Only runs in production)
  eleventyConfig.addTransform("htmlmin", function (content, outputPath) {
    if (process.env.ELEVENTY_ENV === "production" && outputPath && outputPath.endsWith(".html")) {
      let minified = htmlmin.minify(content, {
        useShortDoctype: true,
        removeComments: true,
        collapseWhitespace: true,
        minifyCSS: true,
        minifyJS: true
      });
      return minified;
    }
    return content;
  });

  // Eleventy config
  return {
    dir: { input: ".", includes: "_includes", data: "_data", output: "_site" },
    serverOptions: { liveReload: false, domDiff: false, port: 8087 },
  };
};
