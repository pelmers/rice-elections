# CS for Election Information Panel
informationForm = null
define((require) ->
    $ = require('jquery')
    TextInput = require('ui/text-input')
    DateTimeRangeInput = require('ui/datetime-range-input')
    Button = require('ui/button')
    AjaxLink = require('ajax-link')
    ZeroClipboard = require('ZeroClipboard')

    class InformationForm
        constructor: ->
            @id = ""

            # Election name
            @name = new TextInput($('#name'), {
                required: true
                controlGroup: $('#name').parent().parent()
            })

            # Initialize voting time input
            rangeOptions =
                language: 'en'
                pickTime: true
                pick12HourFormat: true
                pickSeconds: false
                required: true
                pastAllowed: false
                controlGroup: $('#start-date-time').parent().parent()
            @votingTime = new DateTimeRangeInput(
                $('#start-date-time'), $('#end-date-time'), rangeOptions)

            # Input Choice: The delay in results to public
            @resultDelay = $('#result-delay')

            # Checkbox: Whether the election is universal
            @universal = $('#universal-election')

            # Checkbox: Whether the election is hidden
            @hidden = $('#hidden-election')

            # Election link modal
            @linkModal = new LinkModal()

            # Submit Button
            $('#election-submit').click(@sync)
            @submitBtn = new Button($('#election-submit'))
            @_link = new AjaxLink('/admin/organization/election/information',
                                  {postView: @submitBtn})

        toJSON: =>
            json =
                id: @id
                name: @name.getVal()
                times: @votingTime.toJSON()
                result_delay: @getResultDelay()
                universal: @universal.prop('checked')
                hidden: @hidden.prop('checked')
            for key, value of json
                return null if value == null
            return json

        setFromJSON: (json) =>
            console.log(json)
            @id = json.id
            @name.setVal(json.name)
            @votingTime.setFromJSON(json.times)
            @setResultDelay(json.result_delay)
            @universal.prop('checked', json.universal)
            @hidden.prop('checked', json.hidden)

        sync: =>
            json = @toJSON()
            if @submitBtn.disabled() or not json
                return

            @_link.post(json, @setFromJSON)

        getResultDelay: => parseInt(@resultDelay.val())

        setResultDelay: (delay) =>
            if not $("#result-delay option[value=#{delay}]")
                @resultDelay.append(
                    "<option id='custom' value='#{delay}'>#{delay}</option>")
            @resultDelay.val(delay).change()

    class LinkModal
        constructor: ->
            @el = $('#modal-election-link')
            @link = $('#modal-election-link-text')
            @linkHref = ''
            @copyLink = $('#modal-election-link-copy')
            @clip = new ZeroClipboard(@copyLink, {moviePath: "/static/js/shared/ZeroClipboard.swf", text: 'Hello!'})

            @clip.on 'complete', (client, args) ->
                alert("Copied text to clipboard: #{args.text}")
            # @copyLink.click(@copy)

        load: (id) ->
            host = window.location.host
            @linkHref = "http://#{host}/vote/cast-ballot?id=#{id}"
            linkText = $('<a>', 'href': @linkHref).text(@linkHref)
            @link.text(@linkHref)
            @copyLink.attr('data-clipboard-text', @linkHref)
            @clip = new ZeroClipboard(@copyLink, {moviePath: "/static/js/shared/ZeroClipboard.swf", text: 'Hello!'})

        show: -> @el.modal('show')

    informationForm = new InformationForm()
    console.log(informationForm)

)