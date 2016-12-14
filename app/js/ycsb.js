loadYCSBSummaryChart = function(measurements) {
  //    var summarypath = measurements[0].rundir+"/data/final/ycsbsummary.csv";
  var summarypath ="../data/final/ycsbsummary.csv";
  $.ajax({
    type: "GET",
    url: summarypath,
    dataType: "text",
    success: function(data) {
      var data = data.split("\n").map(function (row) {
        return row.split(",");
      });
      processYCSBChart(data,measurements)
    },
    error: function(request, status, error) {
      console.log(status);
    }
  });
};

processYCSBChart = function(data,measurements) { 
  var colors = ['#ff0000', '#00ff00', '#0000ff', '#eeeeee']
  var chart = c3.generate({
    bindto: '#id_summary',
    data: {
      x: 'runid',
      columns: data,
      type: 'bar',
      labels: {
        format: function(v, id, i, j) {
          return "ITER " + id + " = " + parseInt(v) + " ops/sec";
        }
      },
      color: function(inColor, data) {
        if (data.index !== undefined) {
          return d3.rgb(colors[data.index%colors.length]).darker(data.id - 1);
        }
        return inColor;
      },
      tooltip: {
        grouped: true
      }
    },
    bar: {

      width: {
        ratio: 0.5         // this makes bar width 50% of length between ticks
      }
    },
    axis: {
      rotated: true,
      x: {
        label: {
          position: 'outer-center',
        },
        type: 'category', // this is needed to load string x value
      }
    },
    legend: {
      show: false,
    },
    interaction: {
      enabled: false
    },
  });
};