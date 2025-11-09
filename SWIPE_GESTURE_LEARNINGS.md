# Swipe Gesture Implementation Learnings

## Overview
This document captures the attempts, challenges, and learnings from implementing swipe-based word selection in the Boggle iOS app. After multiple iterations, we reverted to tap-only input due to fundamental challenges with touch precision and sampling.

## Timeline of Attempts

### Attempt 1: Basic Center-Based Detection (70% Threshold)
**Date:** Early implementation
**Approach:** Detect tiles when finger center is within 70% of tile radius (24.5px from center)

**Implementation:**
```swift
let detectionThreshold = tileRadius * 0.7
let distance = sqrt(pow(tileCenter.x - location.x, 2) + pow(tileCenter.y - location.y, 2))
if distance <= detectionThreshold {
    // Register tile
}
```

**Problem:** Too strict - fast swipes missed tiles even when visually crossing them
**User Feedback:** "Swiped W-I-R-E but only W and I were highlighted"

### Attempt 2: Increased Threshold to 85%
**Approach:** Increased detection radius from 70% to 85% (29.75px from center)

**Mathematical Analysis:**
- Tile size: 70px, radius: 35px
- Detection threshold at 85%: 29.75px from center
- Distance between adjacent tile centers: 78px (70px tile + 8px spacing)
- Safety buffer: 9.25px clearance between detection zones
- **Conclusion:** Should NOT cause accidental adjacent picks

**Problem:** Still missed tiles on diagonal swipes
**Root Cause:** iOS DragGesture.onChanged doesn't fire for every pixel

### Attempt 3: Fix End-of-Swipe Detection
**Approach:** Added location parameter to `endDrag()` to check final tile

**Implementation:**
```swift
.onEnded { value in
    endDrag(at: value.location, in: geometry.size)
}
```

**Problem:** Led to more issues with wrong tile detection
**Insight:** Fixing symptoms rather than root cause

### Attempt 4: Bounds-Based Detection
**Approach:** Changed from center-distance check to tile boundary check (anywhere in 70x70px tile)

**Implementation:**
```swift
let tileLeft = CGFloat(col) * tileWithSpacing + 8
let tileRight = tileLeft + tileSize
// ... similar for top/bottom
guard location.x >= tileLeft && location.x <= tileRight &&
      location.y >= tileTop && location.y <= tileBottom else { return }
```

**Problem:** Even less reliable - detected extra/wrong tiles
**User Feedback:** "No this has become less reliable. I want you to think deeply about the fix now and not try and hack it."

### Attempt 5: DDA Grid Traversal (First Implementation)
**Date:** Latest attempt
**Approach:** Implemented Digital Differential Analyzer (DDA) algorithm to find ALL grid cells crossed by line segments

**Research Findings:**
- Bresenham's algorithm doesn't find ALL crossed cells
- DDA with linear interpolation is standard for grid-based games
- Need to interpolate between sparse iOS samples

**Implementation:**
```swift
// Track last drag point
@State private var lastDragPoint: CGPoint? = nil

// For each new drag point, find all tiles crossed by line segment
let crossedTiles = getTilesCrossed(from: lastDragPoint ?? location, to: location, boardSize: board.count)

// DDA implementation
let dx = x2 - x1
let dy = y2 - y1
let steps = max(abs(dx), abs(dy)) * 2  // Double for finer sampling
for i in 0...Int(steps) {
    let t = CGFloat(i) / steps
    let x = x1 + dx * t
    let y = y1 + dy * t
    // Convert to grid cell and add
}
```

**Problem:** Treated spacing as part of tile - detected wrong tiles
**Observation:** Blue line accurate but H tile incorrectly highlighted when path went through T→O

### Attempt 6: DDA with Spacing Exclusion
**Approach:** Added explicit checks to exclude points falling in 8px spacing gaps

**Implementation:**
```swift
// Check if point is actually WITHIN the tile (not in spacing gap)
let tileLeft = CGFloat(col) * tileWithSpacing
let tileTop = CGFloat(row) * tileWithSpacing

let withinTileX = (adjustedX - tileLeft) < tileSize  // Must be within 70px
let withinTileY = (adjustedY - tileTop) < tileSize  // Must be within 70px

// Only add if point is within bounds AND within tile (not spacing)
if row >= 0 && row < boardSize && col >= 0 && col < boardSize && withinTileX && withinTileY {
    tiles.append(tile)
}
```

**Problem:** Still picked up adjacent tiles that blue line didn't cross
**User Feedback:** "Still seems to pick adjacent cells. Again check the blue line vs green cell"

## Fundamental Issues Identified

### 1. iOS Sampling Sparsity
- `DragGesture.onChanged` does not fire for every pixel
- During fast swipes, samples can be 20-30 pixels apart
- Diagonal swipes particularly problematic - can skip entire tiles

### 2. Spacing Ambiguity
- 8px gaps between 70px tiles create ambiguous zones
- When path crosses gap diagonally, unclear which (if any) tile to register
- Even with "spacing exclusion" logic, near-boundary paths cause issues

### 3. Touch Precision vs User Intent
- Finger contact area is ~40-50px diameter
- User sees blue line (connected samples) but expects tile detection to match visual path
- Visual feedback (blue line) doesn't match actual sample points used for detection
- Users naturally swipe quickly, exacerbating sampling issues

### 4. Coordinate Transformation Complexity
- Must account for:
  - 8px padding around entire grid
  - 70px tile size
  - 8px spacing between tiles
  - Screen coordinate to grid coordinate conversion
- Small errors in any calculation propagate to wrong tile detection

### 5. Edge Cases Are Common
- Fast diagonal swipes (most common user behavior)
- Swipes near tile boundaries
- Swipes that "cut corners" between non-adjacent tiles
- All of these are normal gameplay, not edge cases

## Technical Details

### Tile Layout Constants
```swift
let tileSize: CGFloat = 70        // Actual tile area
let spacing: CGFloat = 8          // Gap between tiles
let padding: CGFloat = 8          // Padding around entire grid
let tileWithSpacing: CGFloat = 78 // Total space per tile
```

### Coordinate Systems
- **Screen space:** Absolute pixel coordinates from gesture
- **Adjusted space:** After subtracting padding
- **Grid space:** Row/column indices (0-3 for 4x4 board)

### Distance Calculations
- Adjacent tile centers: 78px apart
- Diagonal tile centers: ~110px apart (√(78² + 78²))
- Tile radius: 35px
- Detection at 85%: 29.75px radius

## Alternative Approaches Considered

### Option A: Strict Path Following
Only highlight tiles where finger center passes through 70x70 tile area
- **Pro:** Unambiguous, predictable
- **Con:** Requires precise aiming, frustrating for fast gameplay

### Option B: Proximity-Based
Highlight tile closest to each sample point
- **Pro:** Forgiving, catches intended tiles
- **Con:** Can pick up adjacent unintended tiles

### Option C: Revert to Tap-Only
Remove swiping, use only tap input
- **Pro:** Simple, reliable, no ambiguity
- **Con:** Slower gameplay, less fluid

### Option D: Hybrid Closest-Tile
For each sample, find nearest tile center and add if not already added
- **Pro:** More intuitive than boundary checking
- **Con:** Still subject to sampling issues and adjacent-tile problems

## Code Files Modified

### BoggleApp/BoggleApp/GameView.swift
**State Variables Added:**
- `@State private var dragPath: [CGPoint] = []` - Visual feedback
- `@State private var selectedTiles: Set<String> = []` - Highlighting
- `@State private var lastDragPoint: CGPoint?` - DDA interpolation

**Functions Modified:**
- `handleDrag(at:in:)` - Main gesture detection logic
- `endDrag(at:in:)` - End of swipe handling
- `getTilesCrossed(from:to:boardSize:)` - DDA grid traversal helper

**Visual Enhancements:**
- Canvas overlay for blue path drawing
- Green highlighting for selected tiles
- Scale animation on selection

## Decision: Revert to Tap-Only

After 6 major iterations over multiple days, we decided to revert to tap-only input because:

1. **No perfect solution exists** - All approaches have false positives (adjacent tiles) or false negatives (missed tiles)
2. **Complexity vs value** - Hundreds of lines of code for marginal UX improvement
3. **User frustration** - Unreliable behavior worse than slower reliable behavior
4. **Touch input limitations** - Fighting against platform constraints (sparse sampling, large finger size)

## Lessons Learned

### Technical Lessons
1. **iOS gesture sampling is sparse** - Cannot rely on continuous touch data
2. **Spacing matters** - Gaps between UI elements create ambiguous zones
3. **Visual feedback ≠ detection accuracy** - Blue line (interpolated) looks accurate but detection (sampled) is not
4. **Simple solutions often best** - Tap input is predictable and reliable

### Process Lessons
1. **Research before implementing** - Should have researched DDA/grid traversal from the start
2. **Prototype with constraints in mind** - Touch precision limitations should have been considered earlier
3. **User feedback invaluable** - Screenshots and specific examples (T-O-H issue) were crucial
4. **Know when to stop** - After 6 attempts, time to accept fundamental limitations

### UX Lessons
1. **Predictability > cleverness** - Users prefer reliable slow over unreliable fast
2. **Visual feedback can mislead** - Blue line created false expectation of accuracy
3. **Touch is imprecise** - Finger size, sampling rate, and speed all affect detection
4. **Edge cases are common cases** - Fast diagonal swipes are normal gameplay

## Future Considerations

If revisiting swipe functionality:

### Potential Solutions to Explore
1. **Slower gesture sampling** - Reduce MinimumDistance to get more samples
2. **Machine learning** - Train model to predict intended path from sparse samples
3. **Post-swipe correction** - Show preview, let user confirm/correct before submitting
4. **Larger tiles** - Increase from 70px to 90px+ to reduce boundary issues
5. **No spacing** - Remove 8px gaps (tiles touch each other)
6. **Different game mechanic** - Instead of path following, use "swipe direction" to indicate word

### Questions to Answer First
1. How do commercial word games (Word Cookies, Wordscapes, etc.) handle this?
2. Can we get higher-frequency touch samples from iOS?
3. Is there a standard iOS framework/library for this use case?
4. Would users actually prefer swipe over tap in practice?

### Acceptance Criteria for Future Swipe Implementation
Before considering swipe complete, it must:
1. ✅ Detect all tiles that blue visual path crosses (zero false negatives)
2. ✅ Not detect tiles that blue path doesn't cross (zero false positives)
3. ✅ Work reliably for fast diagonal swipes
4. ✅ Pass user testing with 95%+ satisfaction
5. ✅ Handle all boundary/spacing edge cases correctly

## Conclusion

Swipe gesture word selection is deceptively complex. What appears simple ("just detect tiles the finger crosses") involves:
- Sparse touch sampling
- Coordinate transformations
- Grid traversal algorithms
- Spacing ambiguity
- User intent inference
- Visual feedback synchronization

The tap-based approach, while slower, provides:
- 100% reliability
- Zero ambiguity
- Predictable behavior
- Simple implementation
- Better accessibility

**Recommendation:** Stay with tap input unless a compelling solution to the fundamental sampling and spacing issues emerges.

## References

### Research Sources
- SwiftUI DragGesture documentation
- Bresenham's line algorithm
- DDA (Digital Differential Analyzer) grid traversal
- Game development grid-based collision detection

### Related Files
- `BoggleApp/BoggleApp/GameView.swift` - Main implementation
- `TECHNICAL_DEBT.md` - May contain related UI issues

### Git History
Multiple commits across several days exploring different swipe detection approaches. See commit messages containing "swipe", "gesture", or "DDA" for full history.
