# Changes to the extraction gold set

## v1 (Oct 2026): 455 items, 10 papers

Annotated by an LLM (Claude) from the full text of each paper (see `../ANNOTATION_GUIDE.md`).

## v1.1 (Oct 2026): adjudication after the first comparison (run `phase2_flash_lite`)

Added 14 items the papers state that fit the guide's definitions but had been left out
(each row's note ends with "added in adjudication"):

- 1409.1556: learning rate 1e-3 (S=384 nets, localisation fine-tuning).
- 1512.03385: dropout none ("We do not use dropout"); COCO detection mini-batch 8 (RPN) and
  16 (Fast R-CNN), learning rates 0.001 and 0.0001.
- 1706.03762: constituency parsing beam size 21 and length penalty 0.3.
- 1907.11692: 100K and 300K pre-training steps (Table 4).
- 1910.01108: inference batch size 1; Intel Xeon E5-2690 v3 CPU and iPhone 7 Plus (timing).
- 2010.11929: Polyak averaging factor 0.9999.

Removed one alias that matched unrelated metrics ("score" for 1910.01108's GLUE
macro-score). Nothing was removed to suit the system.
