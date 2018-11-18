odoo.define('keypad_pdv.numpad', function (require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var _t = core._t;

	var NumpadKeyboard = PopupWidget.extend({
        template: 'NumberPopupWidget',
        init: function(parent, options) {
            var self = this;

            this._super(parent, options);
            this.inputbuffer = "";

			this.firstinput  = true;
			this.decimal_point = _t.database.parameters.decimal_point;

			// This is a keydown handler that prevents backspace from
			// doing a back navigation. It also makes sure that keys that
			// do not generate a keypress in Chrom{e,ium} (eg. delete,
			// backspace, ...) get passed to the keypress handler.
			this.keyboard_keydown_handler = function(event){
				if (event.keyCode === 8 || event.keyCode === 46) { // Backspace and Delete
					event.preventDefault();

					// These do not generate keypress events in
					// Chrom{e,ium}. Even if they did, we just called
					// preventDefault which will cancel any keypress that
					// would normally follow. So we call keyboard_handler
					// explicitly with this keydown event.
					self.keyboard_handler(event);
				}
			};

            this.keyboard_handler = function(event){
                var key = '';
                var valid = true;

                if (event.type === "keypress") {
                        if (event.keyCode === 13) { // Enter
                            self.click_confirm();
                        } else if ( event.keyCode === 190 || // Dot
                                    event.keyCode === 110 ||  // Decimal point (numpad)
                                    event.keyCode === 188 ||  // Comma
                                    event.keyCode === 46 ) {  // Numpad dot
                            key = self.decimal_separator;
                        } else if (event.keyCode >= 48 && event.keyCode <= 57) { // Numbers
                            key = '' + (event.keyCode - 48);
                        } else if (event.keyCode === 45) { // Minus
                            // key = '-';
                            valid = false;
                        } else if (event.keyCode === 43) { // Plus
                            // key = '+';
                            valid = false;
                        }
                    } else { // keyup/keydown
                        if (event.keyCode === 46) { // Delete
                            key = 'CLEAR';
                        } else if (event.keyCode === 8) { // Backspace
                            key = 'BACKSPACE';
                        }
                    }
                // console.log(event.keyCode);
                if (valid == true) {
                    self.key_numpad(key);
                }
                event.preventDefault();
            };
        },

        key_numpad: function(input){
            var newbuf = this.gui.numpad_input(this.inputbuffer, input, {'firstinput': this.firstinput});

            this.firstinput = (newbuf.length === 0);

            if (newbuf !== this.inputbuffer) {
                this.inputbuffer = newbuf;
                this.$('.value').text(this.inputbuffer);
                // console.log(this.inputbuffer);
            }

        },

        show: function(options){
            options = options || {};

            window.document.body.addEventListener('keypress',this.keyboard_handler);
            window.document.body.addEventListener('keydown',this.keyboard_keydown_handler);

            this._super(options);
            this.inputbuffer = '' + (options.value   || '');
            this.decimal_separator = _t.database.parameters.decimal_point;
            this.renderElement();
            this.firstinput = true;

        },

        hide: function(){
            window.document.body.removeEventListener('keypress',this.keyboard_handler);
            window.document.body.removeEventListener('keydown',this.keyboard_keydown_handler);
            this._super();
        },

        click_numpad: function(event){

            var newbuf = this.gui.numpad_input(
                this.inputbuffer,
                $(event.target).data('action'),
                {'firstinput': this.firstinput});

            this.firstinput = (newbuf.length === 0);

            if (newbuf !== this.inputbuffer) {
                this.inputbuffer = newbuf;
                this.$('.value').text(this.inputbuffer);
                // console.log(this.inputbuffer);
            }
        },
        click_confirm: function(){
            this.gui.close_popup();
            if( this.options.confirm ){
                this.options.confirm.call(this,this.inputbuffer);
            }
        },
    });

    gui.define_popup({name:'number', widget: NumpadKeyboard});


    var PassNumpadKeyboard = NumpadKeyboard.extend({
        renderElement: function(){
            this._super();
            this.$('.popup').addClass('popup-password');
        },
        key_numpad: function(event){
            this._super.apply(this, arguments);
            var $value = this.$('.value');
            $value.text($value.text().replace(/./g, '•'));
        },
        click_numpad: function(event){
            this._super.apply(this, arguments);
            var $value = this.$('.value');
            $value.text($value.text().replace(/./g, '•'));
        },
    });

    gui.define_popup({name:'password', widget: PassNumpadKeyboard});

});
