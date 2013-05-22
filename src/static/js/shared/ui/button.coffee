define ['jquery'], ($) ->
	class Button
        constructor: (@el) ->
        setFromJSON: (json) =>
            if json.type == 'ok'
                @set('disabled btn btn-success', json.message)
            else
                @set('disabled btn btn-danger', json.message or 'Unknown error')
        set: (btnClass, msg) =>
            @el.attr('class', btnClass)
            @el.text(msg)
        disabled: => @el.hasClass('disabled')