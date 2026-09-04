const pluginRss = require("@11ty/eleventy-plugin-rss");
const CleanCSS = require("clean-css");
const Terser = require("terser");
const htmlmin = require("html-minifier-terser");
const { execSync } = require("child_process");
const path = require("path");

module.exports = function(eleventyConfig) {
  eleventyConfig.setUseGitIgnore(false);

  eleventyConfig.addPassthroughCopy({ "css": "css" });
  eleventyConfig.addPassthroughCopy({ "js": "js" });
  eleventyConfig.addPassthroughCopy({ "files": "files" });
  eleventyConfig.addPassthroughCopy("fonts");

  eleventyConfig.addPassthroughCopy({ "img/icons": "img/icons" });
  eleventyConfig.addPassthroughCopy({ "img/optimized": "img/optimized" });
  eleventyConfig.addPassthroughCopy({ "img/showreel": "img/showreel" });
  eleventyConfig.addPassthroughCopy("_includes");

  eleventyConfig.addWatchTarget("css");
  eleventyConfig.addWatchTarget("js");
  eleventyConfig.addWatchTarget("img/showreel");
  eleventyConfig.addWatchTarget("img/projects");

  eleventyConfig.on("beforeBuild", () => {
    const optimizerPath = path.join(__dirname, "scripts", "optimize_assets.py");
    console.log("[Asset Pipeline] Running optimizer before build...");
    try {
      execSync(`python3 "${optimizerPath}"`, { stdio: "inherit" });
    } catch (err) {
      console.error("[Asset Pipeline] Optimizer failed:", err.message);
      process.exit(1);
    }

    const vimeoThumbsPath = path.join(__dirname, "scripts", "fetch_vimeo_thumbs.py");
    try {
      execSync(`python3 "${vimeoThumbsPath}"`, { stdio: "inherit" });
    } catch (err) {
      console.error("[Asset Pipeline] Vimeo thumbnails fetch failed:", err.message);
      process.exit(1);
    }
  });

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

  eleventyConfig.addCollection("tagList", (collectionsApi) => {
    const set = new Set();
    collectionsApi.getAll().forEach(item => (item.data.tags || []).forEach(t => set.add(t)));
    return [...set];
  });

  eleventyConfig.addFilter("cssmin", function(code) {
    return new CleanCSS({}).minify(code).styles;
  });
  eleventyConfig.addFilter("jsmin", function(code) {
    let min = Terser.minify(code);
    return min.error ? code : min.code;
  });
  eleventyConfig.addTransform("htmlmin", async function(content, outputPath) {
    if (outputPath && outputPath.endsWith(".html")) {
      return await htmlmin.minify(content, {
        useShortDoctype: true, removeComments: true, collapseWhitespace: true, minifyCSS: true, minifyJS: true
      });
    }
    return content;
  });

  return {
    dir: { input: ".", includes: "_includes", data: "_data", output: "_site" },
    serverOptions: { liveReload: false, domDiff: false, port: 8087 },
    templateFormats: ["html", "njk", "md"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk"
  };
};
