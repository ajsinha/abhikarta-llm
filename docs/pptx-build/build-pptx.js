const pptxgen = require("pptxgenjs");
const { html2pptx } = require("./html2pptx");

async function buildPresentation() {
  console.log("Building Abhikarta-LLM Presentation...");
  
  // Create a new pptx presentation
  const pptx = new pptxgen();
  pptx.layout = "LAYOUT_16x9";
  pptx.title = "Abhikarta-LLM - Enterprise AI Orchestration Platform";
  pptx.author = "Abhikarta Team";
  pptx.subject = "AI/ML Platform Overview";
  pptx.company = "Abhikarta";
  
  // Define slide files in order
  const slides = [
    "slide01-title.html",
    "slide02-overview.html",
    "slide03-features.html",
    "slide04-architecture.html",
    "slide05-providers.html",
    "slide06-agents.html",
    "slide07-workflows.html",
    "slide08-dashboard.html",
    "slide09-security.html",
    "slide10-getting-started.html",
    "slide11-tech-stack.html",
    "slide12-thankyou.html"
  ];
  
  // Process each slide
  for (let i = 0; i < slides.length; i++) {
    const slideFile = slides[i];
    console.log(`  Processing ${slideFile}...`);
    try {
      await html2pptx(slideFile, pptx);
    } catch (err) {
      console.error(`  Error processing ${slideFile}:`, err.message);
    }
  }
  
  // Save the presentation
  const outputPath = "Abhikarta-LLM-Overview.pptx";
  await pptx.writeFile(outputPath);
  console.log(`\nPresentation saved to: ${outputPath}`);
  
  return outputPath;
}

buildPresentation().catch(err => {
  console.error("Build failed:", err);
  process.exit(1);
});
