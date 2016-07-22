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
});
