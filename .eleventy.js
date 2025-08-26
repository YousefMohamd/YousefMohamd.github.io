module.exports = function(eleventyConfig) {
  // مرّر الملفات الساكنة زي ما هي
  eleventyConfig.addPassthroughCopy({ "img": "img" });
  eleventyConfig.addPassthroughCopy({ "css": "css" });
  eleventyConfig.addPassthroughCopy({ "files": "files" });

  // إعدادات القوالب
  return {
    dir: { input: ".", includes: "_includes", data: "_data", output: "_site" },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
    templateFormats: ["njk","md","html"]
  };
};
