/*
 * Copyright (C) 2016  Dominik George <nik@naturalnet.de>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 * Alternatively, you are free to use this software under any of
 * LGPL-2+, AGPL-3+, Simplified BSD or The MirOS Licence.
 */

MessagesService = function() {
    // contains a set of id: {class: 'alert class', message: 'foo'} objects
    this.msgs = {};

    // Remove the message
    this.remove = function(id) {
        // Clear the timer first, in case we got called manually
        window.timeout.cancel(msgs[id].tid);
        delete msgs[id];
    };

    this.add = function(cls, message) {
        // Find next numeric id
        if (Object.keys(msgs).length > 0) {
            var id = Math.max.apply(null, Object.keys(this.msgs)) + 1;
        } else {
            id = 0;
        }

        // Add desired content with found id
        this.msgs[id] = {
            'class': cls,
            'message': message
        };

        // Add timer to auto-close the message
        var tid = window.timeout(this.remove, 10000, true, id);
        this.msgs[id].tid = tid;
    };
};

Messages = new MessagesService();
