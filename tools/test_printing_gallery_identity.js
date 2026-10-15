#!/usr/bin/env node
"use strict";

const path = require("path");
const runtime = require(path.join(__dirname, "..", "assets", "printing-gallery.js"));

function assert(condition, message){
  if(!condition){
    console.error("FAIL:", message);
    process.exit(1);
  }
}

const canonical = {name:"Reanimate", oracle_id:"oracle-reanimate"};
const base = {
  object:"card", lang:"en", digital:false, games:["paper"], layout:"normal",
  name:"Reanimate", oracle_id:"oracle-reanimate", artist:"Artist",
  image_uris:{normal:"https://cards.scryfall.io/normal/front/a/b/example.jpg", art_crop:"https://cards.scryfall.io/art_crop/front/a/b/example.jpg"}
};
const valid = Array.from({length:15}, (_, index) => ({
  ...base,
  id:`reanimate-${index}`,
  set:index===0?"tmp":`s${index}`,
  set_name:index===0?"Tempest":`Set ${index}`,
  released_at:`${1997+index}-01-01`,
  collector_number:String(100+index),
  illustration_id:`art-${index%7}`,
  image_uris:{
    normal:`https://cards.scryfall.io/normal/front/a/b/reanimate-${index}.jpg`,
    art_crop:`https://cards.scryfall.io/art_crop/front/a/b/reanimate-art-${index%7}.jpg`
  }
}));
const wrong = {
  ...base,
  id:"grave-researcher",
  name:"Grave Researcher",
  oracle_id:"oracle-grave-researcher",
  set:"sos",
  set_name:"Secrets of Strixhaven",
  released_at:"2026-01-01",
  illustration_id:"wrong-art",
  image_uris:{normal:"https://cards.scryfall.io/normal/front/x/y/grave-researcher.jpg", art_crop:"https://cards.scryfall.io/art_crop/front/x/y/grave-researcher.jpg"}
};

assert(runtime.exactIdentity(valid[0], canonical), "a legitimate Reanimate printing should pass exact identity");
assert(!runtime.exactIdentity(wrong, canonical), "Grave Researcher must be rejected even if a search result mentions Reanimate");
assert(!runtime.exactIdentity({...valid[0], oracle_id:"different-oracle"}, canonical), "a different Oracle ID must be rejected");
assert(!runtime.exactIdentity({...valid[0], name:"Reanimate Token"}, canonical), "a different card name must be rejected");

const selected = runtime.selectPrintings([...valid, wrong], "tmp", 12, canonical);
assert(selected.length===12, "a card with more than twelve printings should select exactly twelve");
assert(selected.every(card => card.name==="Reanimate" && card.oracle_id==="oracle-reanimate"), "selection must contain only the requested exact card");
assert(selected[0].set==="tmp", "the original set should remain the first printing");
assert(new Set(selected.map(card => card.id)).size===selected.length, "printing IDs must be unique");
assert(new Set(selected.map(card => card.illustration_id)).size===7, "all available distinct artworks should be represented before same-art reprints");

const few = runtime.selectPrintings(valid.slice(0,5), "tmp", 12, canonical);
assert(few.length===5, "a card with fewer than twelve printings should show all available printings");

const fakeGrid = {dataset:{card:"Reanimate"}};
const validRecords = selected.map(card => ({
  cardName:card.name,
  oracleId:card.oracle_id,
  scryfallId:card.id,
  image:card.image_uris.normal
}));
assert(runtime.recordsAreValid(fakeGrid, validRecords), "valid cached records should pass");
assert(!runtime.recordsAreValid(fakeGrid, [...validRecords.slice(0,2), {cardName:"Grave Researcher", oracleId:"oracle-grave-researcher", scryfallId:"wrong", image:"x"}]), "mixed-card cache must be rejected");

console.log("Printing gallery identity test passed: exact card only, 12 maximum, unique artwork first.");
