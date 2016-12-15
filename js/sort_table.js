$(function(){
  $('table').tablesorter({
      theme: 'green',
      sortMultiSortKey: "shiftKey",
      ignoreCase: true,
      sortInitialOrder: "desc"
  });
});
