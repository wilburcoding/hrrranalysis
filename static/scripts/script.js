window.onload = function () {
  runs = {}
  cval = ""
  function update() {
    fetch("/datalist")
      .then(res => res.json())
      .then(res => {
        runs = res
        $("#runs").html("")
        if (cval == "") {
          cval = Object.keys(res)[0]
        }
        for (var item of Object.keys(res)) {
          $("#runs").append(`
          <option value="${item}" ${item == cval ? "selected" : ""}>${item}</option>
      `)
          $("#fields").css("display", "flex")
        }
        if (runs[cval] == undefined) {
          cval=Object.keys(res)[0]
        }
        $(".slider").attr("max", runs[cval])
        
      })

    $("#sinfo").html($(".slider").val() + "/" + $(".slider").attr("max"))
    for (var i = 0; i < runs[cval] + 1; i++) {
      var img = new Image();
      img.src = "/data/" + cval + "/" + $("#fields").val() + "/" + i + ".png";
    }
  }
  $("#runs").on("change", function () {
    update();
  })
  $("#fields").on("change", function () {
    update();
  })
  $(".slider").on("input", function () {
    $("#sinfo").html($(this).val() + "/" + $(this).attr("max"))
    $("#im").attr("src", "/data/" + cval + "/" + $("#fields").val() + "/" + $(this).val() + ".png")
  })
  $("#runs").on("change", function () {
    cval = $(this).val()
    update()
  })
  update()
  setInterval(update, 4000)


}