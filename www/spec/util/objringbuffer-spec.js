fs = require('fs');
eval(fs.readFileSync('./js/util/objringbuffer.js', 'utf-8'));

describe('ObjRingbuffer', function() {
    it("returns the correct length", function() {
        var b = new ObjRingbuffer(10);
        b.push({});
        b.push({});
        b.push({});
        expect(b.length()).toBe(3);
    });

    it("returns the correct length after rotating", function() {
        var b = new ObjRingbuffer(10);
        b.push({});
        b.push({});
        b.push({});
        b.push({});
        b.push({});
        b.push({});
        b.push({});
        b.push({});
        b.push({});
        b.push({});
        b.push({});
        b.push({});
        expect(b.length()).toBe(10);
    });

    it("returns the correct maximum for a field", function() {
        var b = new ObjRingbuffer(10);
        b.push({a: 5, b: 3});
        b.push({a: 4, b: 8});
        b.push({a: 3, b: 9});
        b.push({a: 6, b: 1});
        b.push({a: 1, b: 4});
        expect(b.max('b')).toBe(9);
    });

    it("returns the correct minimum for a field", function() {
        var b = new ObjRingbuffer(10);
        b.push({a: 5, b: 3});
        b.push({a: 4, b: 8});
        b.push({a: 3, b: 9});
        b.push({a: 6, b: 1});
        b.push({a: 1, b: 4});
        expect(b.min('b')).toBe(1);
    });

    it("returns the correct average for a field", function() {
        var b = new ObjRingbuffer(10);
        b.push({a: 5, b: 3});
        b.push({a: 4, b: 8});
        b.push({a: 3, b: 9});
        b.push({a: 6, b: 1});
        b.push({a: 1, b: 4});
        expect(b.average('b')).toBe(5);
    });

    it("returns the correct maximum for a field after rotating", function() {
        var b = new ObjRingbuffer(10);
        b.push({a: 5, b: 9});
        b.push({a: 4, b: 1});
        b.push({a: 3, b: 3});
        b.push({a: 6, b: 2});
        b.push({a: 1, b: 2});
        b.push({a: 5, b: 3});
        b.push({a: 4, b: 8});
        b.push({a: 3, b: 7});
        b.push({a: 6, b: 2});
        b.push({a: 1, b: 4});
        b.push({a: 1, b: 4});
        expect(b.max('b')).toBe(8);
    });

    it("returns the correct minimum for a field after rotating", function() {
        var b = new ObjRingbuffer(10);
        b.push({a: 5, b: 9});
        b.push({a: 4, b: 1});
        b.push({a: 3, b: 3});
        b.push({a: 6, b: 2});
        b.push({a: 1, b: 2});
        b.push({a: 5, b: 3});
        b.push({a: 4, b: 8});
        b.push({a: 3, b: 7});
        b.push({a: 6, b: 2});
        b.push({a: 1, b: 4});
        b.push({a: 1, b: 4});
        b.push({a: 1, b: 4});
        expect(b.min('b')).toBe(2);
    });

    it("returns the correct average for a field after rotating", function() {
        var b = new ObjRingbuffer(10);
        b.push({a: 5, b: 9});
        b.push({a: 4, b: 1});
        b.push({a: 3, b: 3});
        b.push({a: 6, b: 2});
        b.push({a: 1, b: 2});
        b.push({a: 5, b: 3});
        b.push({a: 4, b: 8});
        b.push({a: 3, b: 7});
        b.push({a: 6, b: 2});
        b.push({a: 1, b: 4});
        b.push({a: 1, b: 4});
        b.push({a: 1, b: 5});
        expect(b.average('b')).toBe(4);
    });

    it("returns the correct fullness", function() {
        var b = new ObjRingbuffer(10);
        expect(b.isFull()).toBe(false);
        b.push({a: 5, b: 9});
        expect(b.isFull()).toBe(false);
        b.push({a: 4, b: 1});
        expect(b.isFull()).toBe(false);
        b.push({a: 3, b: 3});
        expect(b.isFull()).toBe(false);
        b.push({a: 6, b: 2});
        expect(b.isFull()).toBe(false);
        b.push({a: 1, b: 2});
        expect(b.isFull()).toBe(false);
        b.push({a: 5, b: 3});
        expect(b.isFull()).toBe(false);
        b.push({a: 4, b: 8});
        expect(b.isFull()).toBe(false);
        b.push({a: 3, b: 7});
        expect(b.isFull()).toBe(false);
        b.push({a: 6, b: 2});
        expect(b.isFull()).toBe(false);
        b.push({a: 1, b: 4});
        expect(b.isFull()).toBe(true);
        b.push({a: 1, b: 4});
        expect(b.isFull()).toBe(true);
        b.push({a: 1, b: 5});
        expect(b.isFull()).toBe(true);
    });
});
