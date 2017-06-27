#!/bin/csh -f
Genesis2.pl -parse -generate -top top -input \
  ../sb/sb.vp \
  ../cb/cb.vp \
  ../pe_tile/pe_tile.vp \
  \
  ../oldmemtile/mem_tile_sb_cb.vp \
  ../oldmemtile/mem_tile.vp \
  ../oldmemtile/mem.vp \
  ../oldmemtile/top.vp \
  \
  ../pe_new/pe/rtl/test_pe.svp \
  ../pe_new/pe/rtl/test_mult_add.svp \
  ../pe_new/pe/rtl/test_full_add.svp \
  ../pe_new/pe/rtl/test_lut.svp \
  ../pe_new/pe/rtl/test_opt_reg.svp \
  \
  ../pe_tile_new/pe_tile_new.vp

