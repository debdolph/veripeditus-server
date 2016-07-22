/*
 * veripeditus-web - Web frontend to the veripeditus server
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
 * -or-
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/*
 * The ObjRingbuffer class is a special ringbuffer-like object for
 * objects („dictionaries“). It allows pushing of objects with identical
 * attributes and can return various horizontal statistics about them by
 * a common attribute name.
 *
 * Example:
 *
 *  var metrics = new ObjRingbuffer(100);            // Buffer of 100 entries
 *  metrics.push({age: 12, size: 148, weight: 60});
 *  metrics.push({age: 14, size: 166, weight: 55});
 *  metrics.push({age:  8, size: 128, weight: 35});
 *  metrics.push({age: 66, size: 161, weight: 93});
 *  alert(metrics.min('age');                        // minimum age
 *  alert(metrics.average('size');                   // average size
 *  alert(metrics.max('weight');                     // maximum weight
 *
 * Upon reaching the size given in the constructor; it starts dropping
 * old objects from the end.
 */

function ObjRingbuffer(size) {
    this.size = size;
    this.pointer = 0;
    this.objects = [];
}

ObjRingbuffer.prototype.length = function() {
    return this.objects.length;
}

ObjRingbuffer.prototype.isFull = function() {
    return this.objects.length == this.size;
}

ObjRingbuffer.prototype.push = function(obj) {
    this.pointer = (this.pointer + 1) % this.size;
    this.objects[this.pointer] = obj;
}

ObjRingbuffer.prototype.min = function(field) {
    var m = this.objects[0][field];

    for (var i = 0; i < this.objects.length; i++) {
        if (this.objects[i][field] < m) {
            m = this.objects[i][field];
        }
    }

    return m;
}

ObjRingbuffer.prototype.max = function(field) {
    var m = this.objects[0][field];

    for (var i = 0; i < this.objects.length; i++) {
        if (this.objects[i][field] > m) {
            m = this.objects[i][field];
        }
    }

    return m;
}

ObjRingbuffer.prototype.average = function(field) {
    var s = 0;

    for (var i = 0; i < this.objects.length; i++) {
        s += this.objects[i][field];
    }

    return s / this.objects.length;
}

ObjRingbuffer.prototype.last = function() {
    return this.objects[this.pointer];
}
