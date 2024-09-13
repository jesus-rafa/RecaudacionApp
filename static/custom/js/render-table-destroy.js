function render_table_destroy(myTable, mySearch, myCols) {
    var table = $(myTable).DataTable({
      sDom: "rtip",
      pageLength : 5,
      lengthMenu: [5, 10, 20, 50, 100, 'Todos'],
      destroy: true,
      columnDefs: [
        {
          visible: false,
          orderable: false,
          targets: myCols,
        },
      ],
      language: {
        decimal: "",
        emptyTable: "No hay información",
        info: "Mostrando _START_ a _END_ de _TOTAL_ Entradas",
        infoEmpty: "Mostrando 0 to 0 of 0 Entradas",
        infoFiltered: "(Filtrado de _MAX_ total entradas)",
        infoPostFix: "",
        thousands: ",",
        lengthMenu: "Mostrar _MENU_ Entradas",
        loadingRecords: "Cargando...",
        processing: "Procesando...",
        search: "Buscar:",
        zeroRecords: "Sin resultados encontrados",
        paginate: {
          previous: "<i class='mdi mdi-chevron-left'>",
          next: "<i class='mdi mdi-chevron-right'>",
        },
      },
      drawCallback: function () {
        $(".dataTables_paginate > .pagination").addClass("pagination-rounded");
      },
    });
  
    $(".dataTables_length select").addClass("form-select form-select-sm"),
      $(".dataTables_length select").removeClass(
        "custom-select custom-select-sm"
      ),
      $(".dataTables_length label").addClass("form-label");
  
    $(mySearch).on("keyup click", function () {
      table.tables().search($(this).val()).draw();
    });
  
    table.on("click", "thead tr td", function (event) {
      let indexColumn = $(this).closest("td").index();
  
      $("thead > tr  > td").each(function (index, td) {
        this.classList.remove("negrita");
      });
  
      if ($.inArray(parseInt(indexColumn), myCols) === -1)
        $(this).closest("td").addClass("negrita");
    });
  }
  