define ['jquery'], ($) ->
	class Button
        constructor: (@el) ->
        setText: (txt) =>
            @el.text(txt)
        setType: (type) =>
            @el.removeClass('btn-primary btn-success btn-danger')
            @el.addClass("btn-#{type}")
        disabled: => @el.hasClass('disabled')
        enable: => @el.removeClass('disabled')
        disable: => @el.addClass('disabled')

        setFromJSON: (json) =>
            if json.type == 'ok'
                @setType('success')
            else
                @setType('danger')
            @setText(json.message)
            @disable()