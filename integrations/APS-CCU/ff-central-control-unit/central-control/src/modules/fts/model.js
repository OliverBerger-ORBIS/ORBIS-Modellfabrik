"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Direction = void 0;
/**
 * The direction of a turn action.
 */
var Direction;
(function (Direction) {
    /** Turns the FTS counterclockwise by 90° */
    Direction["LEFT"] = "LEFT";
    /** Turns the FTS clockwise by 90° */
    Direction["RIGHT"] = "RIGHT";
    /** Turns the FTS by 180° to face backwards */
    Direction["BACK"] = "BACK";
})(Direction = exports.Direction || (exports.Direction = {}));
