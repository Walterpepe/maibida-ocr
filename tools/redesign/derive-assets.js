#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const ROOT = path.resolve(__dirname, "..", "..");
const OUT = path.join(ROOT, "cn", "images", "redesign");

const assets = [
  {
    source: "cn/testimg/mjbh1.webp",
    output: "hero-monitor-lineup.webp",
    crop: { left: 0, top: 0, width: 1600, height: 530 }
  },
  {
    source: "cn/testimg/mjbh1.webp",
    output: "product-monitor.webp",
    crop: { left: 0, top: 0, width: 560, height: 530 }
  },
  {
    source: "cn/images/home-banner/ml/en-US/banner-02.webp",
    output: "product-camera.webp",
    crop: { left: 950, top: 100, width: 970, height: 970 }
  },
  {
    source: "cn/images/home-banner/ml/en-US/banner-03.webp",
    output: "product-inline.webp",
    crop: { left: 950, top: 100, width: 970, height: 900 }
  },
  {
    source: "cn/testimg/lm1.webp",
    output: "product-sorter.webp",
    crop: { left: 0, top: 0, width: 685, height: 470 }
  },
  {
    source: "cn/images/home-banner/ml/en-US/banner-05.webp",
    output: "product-feeder.webp",
    crop: { left: 1110, top: 60, width: 810, height: 1020 }
  },
  {
    source: "cn/images/home-banner/ml/en-US/banner-02.webp",
    output: "technology-camera.webp",
    crop: { left: 80, top: 230, width: 1760, height: 850 }
  }
];

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  for (const asset of assets) {
    const source = path.join(ROOT, asset.source);
    const target = path.join(OUT, asset.output);
    await sharp(source)
      .extract(asset.crop)
      .resize({
        width: Math.min(asset.crop.width, 2000),
        withoutEnlargement: true
      })
      .webp({ quality: 88, effort: 6 })
      .toFile(target);
    console.log(
      `${asset.output}: ${fs.statSync(target).size} bytes from ${asset.source}`
    );
  }
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
