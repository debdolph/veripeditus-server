/*
 * Taken from https://github.com/gregallensworth/Leaflet
 * Kudos to Greg Allensworth ☺!
 */
L.LatLng.prototype.bearingTo = function(other) {
    var d2r = L.LatLng.DEG_TO_RAD;
    var r2d = L.LatLng.RAD_TO_DEG;
    var lat1 = this.lat * d2r;
    var lat2 = other.lat * d2r;
    var dLon = (other.lng - this.lng) * d2r;
    var y = Math.sin(dLon) * Math.cos(lat2);
    var x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
    var brng = Math.atan2(y, x);
    brng = parseInt(brng * r2d);
    brng = (brng + 360) % 360;
    return brng;
};
