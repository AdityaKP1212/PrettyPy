$(document).ready(function(){
    $('.sidenav').sidenav();

    $('.tooltipped').tooltip();
    
    $('.datepicker').each(function(){
      console.log(this);
      if($(this).attr('id') == "start"){
        setDatePicker($(this), startDatePickerOnSelect, $("#end"));
      }
      else if($(this).attr('id')== "end"){
        setDatePicker($(this), indexEndDatePickerOnSelect);
      }
      else if($(this).attr('id') == "start1"){
        setDatePicker($(this), startDatePickerOnSelect, $("#end1"));
      }
      else if($(this).attr('id') == "start2"){
        setDatePicker($(this), startDatePickerOnSelect, $("#end2"));
      }
      else if($(this).attr('id') == "end1"){
        setDatePicker($(this), insightEnd1DateOnSelect, $("#start2"));
      }
      else if($(this).attr('id') == "end2"){
        setDatePicker($(this), insightEnd2DateOnSelect);
      }
      
    });

    $('.trantrow').click(function(){
      var mid = $(this).attr("data-mid");
      var start = $("#start").val();
      var end = $("#end").val();
      var url = "http://127.0.0.1:5000" + "/getinsights/"+mid +"?start=" + start + "&end="+ end;
      console.log(mid, url);
      getAjax(url, successBasicInsights, failBasicInsights);
    });

    if($("#indexChart").length > 0){
      let data = {
        labels : JSON.parse(idxlabels),
        transactions : JSON.parse(idxtransactions),
        pageViews : JSON.parse(idxpageViews)
      };
      console.log(data);
      loadBasicCharts(data, $("#indexChart"), true);
    }

    if($("#insightChart").length > 0){
      let data = {
        labels : JSON.parse(idxlabels),
        transactions1 : JSON.parse(idxtransactions1),
        pageViews1 : JSON.parse(idxpageViews1),
        transactions2 : JSON.parse(idxtransactions2),
        pageViews2 : JSON.parse(idxpageViews2)
      };
      console.log(data);
      loadComprehensiveChars(data, $("#insightChart"));
    }

    if($(".areaCharts").length > 0){
      loadAreaCharts($(".areaCharts"));
    }
});

function setMaxDateForPrevDatepickers(date){
  console.log(date);
  let prevDatepickerEles = [$("#start2"), $("#end2")];
  prevDatepickerEles.forEach(function(ele){
    if(ele.length > 0 && !jQuery.isEmptyObject(M.Datepicker.getInstance(ele))){
      let prevpicker = M.Datepicker.getInstance(ele);
      prevpicker.options.maxDate = new Date(date);
    }
  });
}


function startDatePickerOnSelect(date, endEle){
  console.log(date);
  let formattedDate = [date.getFullYear(), date.getMonth()+1, date.getDate()].join('-');
  if(endEle.length > 0 && !jQuery.isEmptyObject(M.Datepicker.getInstance(endEle))){
    let endpicker = M.Datepicker.getInstance(endEle);
    endpicker.options.minDate = new Date(formattedDate);
  }
  if(endEle.attr('id') == "end1"){
    setMaxDateForPrevDatepickers(formattedDate);
  }
}

function indexEndDatePickerOnSelect(date){
  console.log(date);
  if($(this).attr("data-refresh") == "true"){
    refreshIndex(date);
  }else{
    $(this).attr("data-refresh", "true");
  }
}

function insightEnd1DateOnSelect(date){
  console.log(date);
}

function refreshInsights(prevEndDate){
  let start1 = $("#start1").val();
  let end1 = $("#end1").val();
  let start2 = $("#start2").val();
  let endmm = prevEndDate.getMonth()+1;
  let enddd = prevEndDate.getDate();
  let end2 = [prevEndDate.getFullYear(), (endmm > 9 ? '' : '0') + endmm, (enddd > 9 ? '' : '0') + enddd].join('-');
  window.location = window.location.origin + window.location.pathname + "?start1=" + start1 + "&end1=" + end1 + "&start2=" + start2 + "&end2=" + end2;
}

function insightEnd2DateOnSelect(date){
  console.log(date);
  if($(this).attr("data-refresh") == "true"){
    refreshInsights(date);
  }else{
    $(this).attr("data-refresh", "true");
  }
}

function setDatePicker(ele, onSelectFunction, endEle){
  ele.datepicker(
    {
      "setDefaultDate":true, 
      "defaultDate": new Date(ele.attr("data-defdate")),
      "minDate": new Date($('#periodcon').attr("data-mindate")),
      "maxDate": new Date($('#periodcon').attr("data-maxdate")),
      "format" : "yyyy-mm-dd",
      "showClearBtn": true,
      "autoClose": true,
      "onSelect": function(date){
        onSelectFunction(date, endEle);
      },
      "onClose": function(){
        if(endEle != undefined){
          endEle.datepicker("open");
        }
      }
    });
    ele.datepicker("setDate", new Date(ele.attr("data-defdate")));
}

function refreshIndex(endDate){
  let start = $("#start").val();
  let endmm = endDate.getMonth()+1;
  let enddd = endDate.getDate();
  let end = [endDate.getFullYear(), (endmm > 9 ? '' : '0') + endmm, (enddd > 9 ? '' : '0') + enddd].join('-');
  window.location = window.location.origin + "?start=" + start + "&end=" + end;
}

function loadBasicCharts(data, ele, idx = false){
  let ctx = ele;
  let start = $("#start").val();
  let end = $("#end").val();
  let title = '';

  if(idx){
    title = 'Overall ';
  }
  title = title + 'Trend from ' + start + ' to ' +  end;

  let myChart = new Chart(ctx, {
      type: 'line',
      data: {
          labels: data.labels,
          datasets: [{
              label: 'Transactions',
              data: data.transactions,
              fill: false,
              borderColor: 'rgb(0, 150, 140)',
              backgroundColor: 'rgb(0, 150, 140)'
            },
            {
              label: 'PageViews',
              data: data.pageViews,
              fill: false,
              borderColor: 'rgb(238,110,115)',
              backgroundColor: 'rgb(238,110,115)',
              pointStyle: 'triangle',
              pointRadius: 6,
            }
          ]
      },
      options: {
        animation: false,
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: title
          },
          tooltip:{
            position: 'nearest'
          }
        },
        interaction: {
          intersect: false,
          mode: 'index',
        },
        scales: {
            x:{
              display: true,
              title: {
                display: true,
                text: 'Day'
              }
            },
            y: {
                display: true,
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Count'
                }
            }
        }
      }
  });
}

function successBasicInsights(data){
  console.log(data);
  if(!jQuery.isEmptyObject(data) && data["status"] == "200"){
    $("#merchantmodal").html(data["html"]);
    loadBasicCharts(data, $('#myChart'));
    $("#merchantmodal").modal();
    $("#merchantmodal").modal("open");
  }
  else{
    console.log("error in input data");
  }
}

function failBasicInsights(data){
  console.log("something went wrong");
}

function addPreloader(){
  $("#preloader-overlay").css("display", "block");
  $(".preloader-wrapper").css("display", "block");
}

function removePreloader(){
  $("#preloader-overlay").css("display", "none");
  $(".preloader-wrapper").css("display", "none");
}

function getAjax(url, successcallback, failcallback){
  $.ajax({
    url: url,
    type: 'get',
    dataType: 'json',
    beforeSend: addPreloader()
  })
  .done(function(data){
    successcallback(data);
  })
  .fail(function(data) {
    failcallback(data);
  })
  .always(function() {
    removePreloader();
  });
}

function postAjax(url, data, successcallback, failcallback){
  $.ajax({
    url: url,
    type: 'post',
    dataType: 'json',
    data: data,
    beforeSend: addPreloader()
  })
  .done(function(data){
    successcallback(data);
  })
  .fail(function(data) {
    failcallback(data);
  })
  .always(function() {
    removePreloader();
  });
}

function loadComprehensiveChars(data, ele){
  let ctx = ele;
  let start1 = $("#start1").val();
  let end1 = $("#end1").val();
  let start2 = $("#start2").val();
  let end2 = $("#end2").val()
  let title = 'Trend from ' + start1 + ' to ' + end1 + ' compared to ' + start2 + ' to ' + end2;

  let myChart = new Chart(ctx, {
      type: 'line',
      data: {
          labels: data.labels,
          datasets: [{
              label: 'P1 Transactions',
              data: data.transactions1,
              fill: false,
              borderColor: 'rgb(0, 150, 140)',
              backgroundColor: 'rgb(0, 150, 140)'
            },
            {
              label: 'P1 PageViews',
              data: data.pageViews1,
              fill: false,
              borderColor: 'rgb(238,110,115)',
              backgroundColor: 'rgb(238,110,115)',
              pointStyle: 'triangle',
              pointRadius: 6,
            },
            {
              label: 'P2 Transactions',
              data: data.transactions2,
              fill: false,
              borderColor: 'rgb(0, 150, 140)',
              borderDash: [5,5]
            },
            {
              label: 'P2 PageViews',
              data: data.pageViews2,
              fill: false,
              borderColor: 'rgb(238,110,115)',
              pointStyle: 'triangle',
              pointRadius: 6,
              borderDash: [5,5]
            }
          ]
      },
      options: {
        animation: false,
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: title
          },
          tooltip:{
            position: 'nearest'
          }
        },
        interaction: {
          intersect: false,
          mode: 'index',
        },
        scales: {
            x:{
              display: true,
              title: {
                display: true,
                text: 'Day'
              }
            },
            y: {
                display: true,
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Count'
                }
            }
        }
      }
  });
}

function loadAreaChartWithData(ele, data, isPositive){
  let color = 'rgb(238,110,115)';
  if(isPositive){
    color = 'rgb(0, 150, 140)';
  }
  let myChart = new Chart(ele, {
    type: 'line',
    data: {
        labels: ['1', '2', '3', '4', '5'],
        datasets: [{
            data: data,
            fill: 'start',
            borderColor: color,
            backgroundColor: color,
            pointRadius: 0
          },
        ]
    },
    options: {
      animation: false,
      elements:{
        line:{
          tension:0.6
        }
      },
      plugins: {
        legend:{
          display: false,
        },
        title: {
          display: false,
        },
        tooltip:{
          enabled: false,
        }
      },
      scales: {
          x:{
            display: false,
          },
          y: {
              display: false,
          }
      }
    }
});
}


function loadAreaCharts(eles){
  let positiveData = [1,5,9,5,15];
  let negativeData = [15,5,9,5,1]
  $.each(eles, function(){
    if($(this).attr("data-change") == "increase"){
      loadAreaChartWithData($(this), positiveData, true);
    }
    else{
      loadAreaChartWithData($(this), negativeData, false);
    }
  });
}