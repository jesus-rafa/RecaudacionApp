function blockInteraction(boton, panel = null) {
    if (panel != null)
        $(`#${panel}`).block({ message: null });
    else
        $(".panel").block({ message: null });

    $(boton).find('.loading-indicator').show();
}


function unblockInteraction(boton, panel = null) {
    if (panel != null)
        $(`#${panel}`).unblock({ message: null });
    else
        $(".panel").unblock();

    $(boton).find('.loading-indicator').hide();
}

/*Función para sumar o restar días a una fecha:
* Parámetros de la función :
*  - fecha => new Date('2023-04-21') (campo formato fecha corta YYYY-mm-dd)
*  - dias => 12 ó -7 (campo númerico)
* 
* Retorna la fecha en formato dd/mm/YYYY => 21/04/2023
*/
function sumarDiasFecha(fecha, dias) {
    let fecha_mas_dias = fecha.setDate(fecha.getDate() +  dias);

    let formato_fecha = new Date(fecha_mas_dias);
    return formato_fecha.getDate().toString().padStart(2, '0') + '/' + (formato_fecha.getMonth() + 1).toString().padStart(2, '0') + '/' +  formato_fecha.getFullYear();
}
