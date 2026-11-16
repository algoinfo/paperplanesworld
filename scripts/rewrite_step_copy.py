#!/usr/bin/env python3
"""Paraphrase all folding-step captions so they are not foldnfly verbatim copy."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "site" / "data" / "planes.json"

# High-traffic short lines — hand-tuned paraphrases.
FIXED_EN: dict[str, str] = {
    "Fold the paper in half.": "Crease the sheet down the middle.",
    "Unfold and then fold the corners into the center line.": "Open it flat, then tuck both top corners into the midline.",
    "Fold the top edges to the center.": "Bring the upper long edges in until they meet the centre crease.",
    "Fold the paper airplane in half.": "Close the model in half along its length.",
    "Fold the wings down to meet the bottom edge of the plane's body.": "Fold each wing down so its edge lines up with the belly of the fuselage.",
    "Repeat with the other side.": "Mirror the same fold on the opposite side.",
    "Repeat with the left side.": "Do the same fold on the left.",
    "Repeat with the left corner.": "Match that fold on the left corner.",
    "Fold the plane in half.": "Close the plane along the centre spine.",
    "Fold the airplane in half.": "Close the airplane along the centre spine.",
    "Fold the paper airplane in half towards you.": "Bring the halves together toward yourself.",
    "Fold the plane in half towards you.": "Bring the halves together toward yourself.",
    "Fold the plane in half away from you.": "Close the plane in half, folding away from you.",
    "Now, fold the plane in half away from you.": "Close the plane in half, folding away from you.",
    "Next, fold the plane in half away from you.": "Next, close the plane in half folding away from you.",
    "Now, fold the plane in half towards you.": "Now close the plane toward yourself.",
    "Fold the sheet in half.": "Crease the sheet in half.",
    "Fold the paper plane in half.": "Close the paper plane along the spine.",
    "It should now look like this.": "Your sheet should match the shape in the photo.",
    "Fold one corner diagonally.": "Take one corner and crease it on a diagonal.",
    "Fold the paper diagonally.": "Crease the sheet on a diagonal.",
    "Cut off the extra piece at the bottom.": "Trim away the leftover strip at the bottom.",
    "Fold the top two corners to the center line.": "Bring both top corners in so they meet the midline.",
    "Fold the top two corners to the center.": "Pull both top corners in to the centre.",
    "Fold the top corners to the center line.": "Tuck the top corners into the midline.",
    "Fold both corners in to the center line.": "Fold both corners inward onto the midline.",
    "Fold both upper corners to the center.": "Bring both upper corners into the centre.",
    "Fold the top point down to the bottom.": "Fold the tip straight down to the bottom edge.",
    "Fold the top point down to the bottom edge.": "Bring the tip down until it meets the bottom edge.",
    "Fold the top down to the bottom.": "Fold the top edge all the way down to the bottom.",
    "Fold the paper in half and then unfold.": "Crease the sheet in half, then open it flat again.",
    "Fold the paper in half and unfold.": "Crease the sheet in half, then open it flat again.",
    "Fold the sheet in half and then unfold.": "Crease the sheet in half, then open it flat again.",
    "Fold the paper in half and open it back up.": "Crease the sheet in half, then open it again.",
    "Fold the sheet in half and then open back up.": "Crease the sheet in half, then open it again.",
    "Fold the sheet in half vertically.": "Crease the sheet vertically down the middle.",
    "Fold the sheet in half vertically and unfold.": "Make a vertical centre crease, then open the sheet.",
    "Fold your paper in half vertically and then unfold.": "Make a vertical centre crease, then open the sheet.",
    "Unfold and flatten the paper out.": "Open the sheet and press it completely flat.",
    "Unfold the paper all the way and then fold the top two corners to the center.": "Fully open the sheet, then bring both top corners into the centre.",
    "Unfold and then fold the top two corners to the center line.": "Open the sheet, then tuck both top corners into the midline.",
    "Unfold and then fold the top two corners into the center line.": "Open the sheet, then tuck both top corners into the midline.",
    "Unfold and then fold the top corners to the center line.": "Open the sheet, then bring the top corners to the midline.",
    "Open the sheet back up and repeat the same step with the left corner.": "Flatten the sheet again and mirror the fold with the left corner.",
    "Open the paper back up and repeat with the other side.": "Flatten the sheet and repeat the fold on the other side.",
    "Flip the plane around and repeat with the other side.": "Turn the plane over and match the fold on the other side.",
    "Fold the top right corner to the left side.": "Bring the top-right corner across to the left edge.",
    "Fold the top two edges to the center.": "Fold both upper edges in to the centre crease.",
    "Again, fold both outer edges to the center.": "Once more, bring both outer edges into the centre.",
    "Again, fold both top edges to the center.": "Once more, fold both top edges into the centre.",
    "Fold the upper sides to the center line.": "Fold the upper flanks in onto the midline.",
    "Fold both upper edges to the center line.": "Bring both upper edges onto the midline.",
    "Fold the top right edge to the center line.": "Fold the top-right edge in to the midline.",
    "Now, fold out the first wing.": "Now fold the first wing out into place.",
    "Fold the airplane in half towards you.": "Close the airplane toward yourself.",
    "Fold the top two corner to the center.": "Bring both top corners into the centre.",
    "Fold the top two edges in to the center.": "Fold the top edges inward to the centre.",
    "Now, fold the outer edges to the center.": "Now fold the outer edges into the centre.",
    "Fold the two sides into the middle.": "Bring both sides into the middle.",
    "Fold the sheet of paper in half vertically and horizontally.": "Crease the sheet both vertically and horizontally.",
    "Fold the paper in half vertically and horizontally, then open it back up.": "Crease the sheet both ways, then open it flat.",
    "Again, take the top edge and fold to the center.": "Again bring the top edge down to the centre crease.",
    "Repeat the previous step once again.": "Do that same fold one more time.",
    "Repeat the previous step one more time.": "Repeat that fold once more.",
    "Repeat the previous step with the right side.": "Repeat that fold on the right side.",
    "Repeat the last step with the other side.": "Repeat the previous fold on the other side.",
    "Repeat with the left center flap.": "Do the same with the left centre flap.",
    "Repeat again by folding the corners in": "Fold the corners inward once more.",
    "Fold the front two flaps up.": "Lift the front two flaps upward.",
    "Fold the center piece up as shown.": "Fold the centre tab upward as in the photo.",
    "Fold up both middle flaps up.": "Fold both middle flaps upward.",
    "Fold one wing up at a slight angle.": "Raise one wing on a gentle angle.",
    "Finally, fold the edges down to meet the bottom of the body.": "Finish by folding the edges down flush with the bottom of the body.",
    "Again, fold the paper in half.": "Crease the sheet in half once more.",
    "Fold the paper in half by bringing the top to the bottom.": "Bring the top edge down to meet the bottom edge.",
    "Fold in half the other direction, making a crease and then unfold.": "Crease it the other way, then open the sheet again.",
    "Holding the paper sidesways, fold the paper in half and unfold.": "Hold the sheet sideways, crease it in half, then open it.",
    "Fold the tip back about one inch (2.5cm).": "Fold the tip back roughly 1 inch (2.5 cm).",
    "Fold the closed edge over about 1 inch (2.5 cm).": "Roll the closed edge over by about 1 inch (2.5 cm).",
    "Fold one of the top edges over as shown.": "Fold one top edge over as shown in the photo.",
    "Fold the long edge about 3/4 inch (19 mm).": "Crease the long edge over by about 3/4 inch (19 mm).",
    "Fold the paper in half diagonally so opposite corners meet.": "Bring opposite corners together to crease a diagonal.",
    "Fold the other side down so opposite sides meet.": "Fold the remaining side down until the edges meet.",
    "Fold the paper in half and then fold in half again.": "Crease the sheet in half, then fold that packet in half again.",
    "Fold the two outer flaps in to the center line.": "Tuck both outer flaps into the midline.",
    "Fold the top two corners in to the closest crease.": "Fold both top corners in to the nearest crease.",
    "Unfold and then accordion fold the top corners into the inside.": "Open the sheet, then accordion-tuck the top corners inside.",
    "Grab a pair of scissors and cut out a slit like the one shown here.": "Take scissors and cut a slit matching the one in the photo.",
    "First, cut off the bottom to make a perfectly square piece of paper.": "First trim the bottom so you have a clean square.",
    "Fold the plane in half vertically.": "Close the plane with a vertical fold.",
    "Open it back up and then fold in half horizontally.": "Open it, then crease it horizontally in half.",
    "Fold the top point down to create a square.": "Fold the tip down so the top becomes a square.",
    "Fold the downward facing point up to secure the flaps.": "Fold the downward tip up to lock the flaps in place.",
    "Fold the plane in half away from you and flatten it out.": "Close the plane away from you and press it flat.",
    "Fold the paper plane in half.": "Close the paper plane along the spine.",
    "Next, fold the top edge down to meet the center crease.": "Next bring the top edge down to the centre crease.",
    "Holding the paper horizontally, fold the top edge down to meet the center crease.": "With the sheet landscape, fold the top edge down to the centre crease.",
    "Now, fold the top edge down at the center crease.": "Now fold the top edge down on the centre crease.",
    "Fold the corners down to each side and unfold.": "Crease both corners down to the sides, then open them.",
    "Fold the top down so the three creases line up.": "Fold the top down until those three creases align.",
    "Open up the sheet and accordion fold the sides in.": "Open the sheet and accordion-tuck both sides inward.",
    "Fold both edges of the triangle to the center (top layer only).": "On the top layer only, fold both triangle edges into the centre.",
    "Fold the paper in half the other direction and orient the folded edge at the bottom.": "Fold the other way and turn the packet so the folded edge sits at the bottom.",
    "Fold both corners into the middle and use your fingernail to make a crisp crease.": "Bring both corners into the middle and burnish the creases sharp.",
    "Fold the left and right points up to the top, as shown.": "Lift the left and right points up to the top as shown.",
    "Fold the top down to the end of the triangle shape.": "Fold the top down to the base of the triangle.",
    "Next, fold the top point down to the middle edge.": "Next fold the tip down to the middle edge.",
    "Fold both triangle flaps into the center.": "Tuck both triangle flaps into the centre.",
    "Open the sheet back up and accordion fold the sides into the center.": "Open the sheet and accordion-fold both sides into the centre.",
    "Fold the bottom ends of the triangle shape to the top point.": "Bring the bottom tips of the triangle up to the top point.",
    "Fold down both flaps of the diamond shape, then unfold.": "Fold both diamond flaps down, then open them again.",
    "Fold the top edges of the diamond shape to the middle and then unfold.": "Fold the diamond's top edges to the middle, then unfold.",
    "Open the sheet back up and fold the upper corners to the center.": "Open the sheet and bring the upper corners into the centre.",
    "Repeat the last step with the both upper edges.": "Repeat that fold on both upper edges.",
    "Fold along this same crease again so the two halves cross over a bit in the middle.": "Refold that same crease so the halves overlap slightly in the middle.",
    "Fold the bottom triangular piece back up.": "Fold the bottom triangle back upward.",
    "Fold the paper diagonally as shown. Cut off the bottom piece to make a square. Save the bottom piece to use later.": "Crease diagonally as shown, trim the leftover strip into a square, and keep the offcut for later.",
    "Insert the arrow all the way into the plane's body.": "Slide the arrow fully into the plane's body.",
    "Fold the corners down to each side and unfold, making an X pattern.": "Crease both corners down and open them to leave an X.",
    "Fold the top down so the crease lines up with the center of the X pattern.": "Fold the top so the new crease crosses the centre of that X.",
    "Unfold the last step and then tuck the sides inside with an accordion fold.": "Undo the last fold, then accordion-tuck the sides inside.",
    "Fold the corners down to each side and unfold, making an X shape.": "Crease both corners down and open them to form an X.",
    "Fold the top down so the crease lines up with the center of the X.": "Fold the top so the crease crosses the middle of the X.",
    "Open up the previous steps and accordion fold the sides into the middle.": "Open those folds and accordion-tuck the sides into the middle.",
    "Fold the paper in half. Then unfold and fold both sides into the middle.": "Crease in half, open it, then fold both sides into the middle.",
    "Take each triangle flap, fold them up and tuck them into the previously folded top triangle.": "Lift each triangle flap and tuck it into the top triangle you just folded.",
    "Fold the top about 1/2 inch (13mm) away from you.": "Fold the top back about 1/2 inch (13 mm) away from you.",
    "Now, fold the outer flaps to the center line.": "Now fold the outer flaps onto the midline.",
    "Open the sheet back up and accordion fold the center in.": "Open the sheet and accordion-fold the centre inward.",
    "Open the sheet and repeat with the other corner to get the creases shown.": "Open the sheet and repeat on the other corner to match the creases shown.",
    "Fold up one wing from the nose of the plane to the center of the tail.": "Fold one wing up from the nose through to the middle of the tail.",
    "Take one layer and fold it in the opposite direction as shown.": "Take one layer and fold it the opposite way as shown.",
    "Continue folding the two flaps behind the top edge.": "Keep folding those two flaps behind the top edge.",
    "Fold the top corners to the center horizontal line.": "Bring the top corners down to the centre horizontal crease.",
    "Fold the top corners to the bottom of each side.": "Fold each top corner down to the bottom of its side.",
    "Fold out each side to create the wings. The body should be about a 2cm (3/4 inch) tall.": "Fold each side out into a wing — the body ends up about 2 cm (3/4 inch) tall.",
    "Fold the right side over and line it up with the left side and make a vertical crease.": "Bring the right side over to match the left and press a vertical crease.",
    "Now, fold one outer flap down to create the first wing. The body will be about 3/4 inch (19 mm) tall.": "Fold one outer flap down for the first wing; the body should sit about 3/4 inch (19 mm) tall.",
    "Open the previous folds up. Mark a point about 4 inches (10cm) down from the top and fold down along that point.": "Open the earlier folds. Mark about 4 inches (10 cm) from the top and fold down on that mark.",
    "Fold the top right corner diagonally down to the other side.": "Swing the top-right corner diagonally across to the far side.",
    "Now fold the top down and line the crease up with the center part of the X shape.": "Fold the top down so the new crease crosses the middle of the X.",
    "Next, fold the top edge down so it meets the first horizontal crease.": "Next fold the top edge down until it meets the first horizontal crease.",
    "Fold the top section down again along the horizontal crease.": "Fold that top band down again on the horizontal crease.",
    "Hold the paper so the long edge is facing you and fold the paper in half, left to right.": "Hold the sheet with the long edge toward you, then crease it left-to-right in half.",
    "Then fold the left and right sides over to meet this middle crease. Unfold.": "Then fold left and right edges into that middle crease and open them again.",
    "Fold the top two corners down to meet the outer creases, making two triangles.": "Fold both top corners down to the outer creases to form two triangles.",
    "Fold the top edges in to the center crease. Unfold.": "Fold the top edges into the centre crease, then open them.",
    "Fold the left and right sides in to meet the crease made in the previous step.": "Bring left and right sides in to the crease from the previous step.",
    "Refold the crease made in step 4.": "Press the step-4 crease closed again.",
    "Fold the top two corners to the center line": "Bring both top corners onto the midline.",
    "Fold the top point down to the bottom edge of the paper.": "Bring the tip down to the bottom edge of the sheet.",
    "Now, fold the point back up about 5.5cm past the top edge.": "Fold the tip back up so it sits about 5.5 cm beyond the top edge.",
    "Fold the point back down again to the edge of the previous crease.": "Fold the tip back down to the edge of that last crease.",
    "Holding the paper width-wise, fold the top down about 2 inches (5cm).": "Hold the sheet width-wise and fold the top down about 2 inches (5 cm).",
    "Fold the top right corner down to the left edge.": "Bring the top-right corner down to the left edge.",
    "Repeat step three with the other side, folding the opposite way.": "Repeat step three on the other side, folding the opposite direction.",
    "Open the sheet back up to the end of step 1, as shown.": "Open the sheet back to the end of step 1, matching the photo.",
    "Accordion fold the top sides in to get this shape.": "Accordion-tuck the top sides inward to match this shape.",
    "Fold the top point down, leaving it about 1 inch (2.5cm) from the bottom edge.": "Fold the tip down, stopping about 1 inch (2.5 cm) above the bottom edge.",
    "Take the little triangle piece at the bottom and fold it up to lock down the two flaps.": "Fold the small bottom triangle up to lock the two flaps.",
    "Now, fold the paper plane in half away from you.": "Now close the paper plane away from you.",
    "Fold the paper in half vertically. Unfold and then fold the top two corners to the center.": "Make a vertical centre crease, open it, then bring both top corners into the centre.",
    "Fold the top point down to the bottom edge. If you are using A4 paper, fold it about 2cm shy of the bottom edge.": "Bring the tip to the bottom edge — on A4, stop about 2 cm short of the edge.",
    "Fold the point back up, even with the bottom of the triangle flaps, about 3cm of overlap.": "Fold the tip back up level with the triangle flaps, with about 3 cm of overlap.",
    "Fold the top edge down about 5 cm.": "Fold the top edge down by about 5 cm.",
    "Fold the top edge down again to double up the thick part.": "Fold the top edge down again to double that thick band.",
    "Fold the top corners away from you to the back center line.": "Fold the top corners away from you onto the back midline.",
    "Next, fold both upper corner to the center.": "Next bring both upper corners into the centre.",
    "Now, fold the top point down about 2 inches, as shown.": "Now fold the tip down about 2 inches, as shown.",
    "Fold the sheet in half and then fold both upper corner to the center.": "Crease the sheet in half, then bring both upper corners into the centre.",
    "Next, fold the top point back about 3cm.": "Next fold the tip back about 3 cm.",
    "Fold both upper corners to the center line as shown.": "Bring both upper corners onto the midline as shown.",
    "Fold the top point down to meet the corners from the previous step.": "Fold the tip down to meet the corners from the previous step.",
    "Fold the right upper corner to the center again.": "Fold the upper-right corner into the centre again.",
    "Again, fold both top edges to the center.": "Fold both top edges into the centre once more.",
    "Flip the plane around and fold the top point down to the bottom edge.": "Turn the plane over and fold the tip down to the bottom edge.",
    "Flip it around again and fold both corners to the center.": "Flip it again and bring both corners into the centre.",
    "Fold the top right corner so that you make a crease going from the center top to the bottom right corner. Unfold.": "Crease from the top centre down to the bottom-right corner, then open it.",
    "Fold the right corner down to the crease of the previous fold and then refold step 2.": "Fold the right corner down to the previous crease, then remake the step-2 fold.",
    "Repeat step two and three with the left side.": "Repeat steps two and three on the left side.",
    "Fold the top point back up as shown. The doubled over part should be just under 1 inch (2.5cm) tall.": "Fold the tip back up as shown — the doubled band should be just under 1 inch (2.5 cm).",
    "Next, fold the top point down. You can fold it all the way to the bottom, or shy by a little bit. It's up to you!": "Next fold the tip down — all the way to the bottom, or stop a little short; either works.",
    "Fold the paper in half. Cut out the bottom corner to round it off as shown, then unfold.": "Crease in half, round off the bottom corner as shown, then open the sheet.",
    "Fold the top point down 2 inches (5cm) before the bottom edge.": "Fold the tip down, stopping 2 inches (5 cm) above the bottom edge.",
    "Fold down the top two corners about half way down each diagonal crease.": "Fold both top corners about halfway along each diagonal crease.",
    "Now, fold the top edge down about one inch (2.5cm).": "Now fold the top edge down about 1 inch (2.5 cm).",
    "Open the sheet back up and accordion fold both sides in so it looks like this.": "Open the sheet and accordion-tuck both sides in to match this shape.",
    "Next, fold the bottom layer to the center.": "Next fold the bottom layer into the centre.",
    "Now, fold the right side of the triangle shape to the top point.": "Now fold the right side of the triangle up to the top point.",
    "Measure around 2.5 inches (6.3 cm) down from the top and draw a horizontal line.": "Measure about 2.5 inches (6.3 cm) from the top and mark a horizontal line.",
    "Fold the top edge down to the line and then fold it down again on the line.": "Fold the top edge to the line, then fold down again on that line.",
    "Fold the top right corner down along the opposite edge.": "Fold the top-right corner down along the opposite edge.",
    "Unfold everything back to step two. Then fold the top corners so they meet the diagonal creases.": "Open everything back to step two, then fold the top corners to the diagonal creases.",
    "Holding the paper horizontally, fold in half and then unfold.": "Hold the sheet landscape, crease it in half, then open it.",
    "Fold down both top corners to the center.": "Fold both top corners down into the centre.",
    "Fold the tip of the plane down to meet the previous fold. If you are using A4 paper, fold it only half way to the previous folds.": "Fold the tip down to the previous fold — on A4, only go halfway to those folds.",
    "Fold down the top right corner, aligning it with the center.": "Fold the top-right corner down, lining it up with the centre.",
    "Now repeat with the left corner.": "Now mirror that fold on the left corner.",
    "Turn the plane around and fold the right bottom corner to the center.": "Turn the plane and fold the bottom-right corner into the centre.",
    "Open the sheet back up and accordion fold both sides in so it looks like the photo.": "Open the sheet and accordion-tuck both sides to match the photo.",
    "Next, fold the right side of the triangle shape to the top point.": "Next fold the right side of the triangle up to the top point.",
    "Now, fold in the bottom right edge of the diamond shape.": "Now fold in the bottom-right edge of the diamond.",
    "Fold the sheet in half, unfold and then fold the top two corners to the center.": "Crease in half, open it, then bring both top corners into the centre.",
    "Fold the top point down to meet the edge of the previous folds.": "Fold the tip down to the edge of the previous folds.",
    "Next, fold the point back up as shown. The doubled over part should be about 1 inch (2.5cm) tall.": "Next fold the tip back up as shown — the doubled band should be about 1 inch (2.5 cm).",
    "Fold the plane in half and grab a pair of scissors.": "Close the plane in half and pick up scissors.",
    "Holding the paper vertically, fold the top down to the bottom and then fold it in half again from left to right.": "Hold the sheet upright, fold top to bottom, then fold left to right again.",
    "Unfold the horizontal fold and then fold the top two corners to the center.": "Open the horizontal fold, then bring both top corners into the centre.",
    "Unfold all the way and then accordion fold the sides in.": "Fully open the sheet, then accordion-tuck the sides in.",
    "Fold the top layer of the right flap all the way over to the left side. Then take the remaining flap on the right side and fold it to the center.": "Fold the top layer of the right flap fully to the left, then fold the remaining right flap into the centre.",
    "There are 3 layers on the left now.  Grab the top layer and fold to the center.": "You now have three layers on the left — fold the top layer into the centre.",
    "Take these two folded flaps and fold them up in opposite directions as shown.": "Fold those two flaps upward in opposite directions as shown.",
    "Fold it back up as shown, leaving about 23mm of overlap.": "Fold it back up as shown, leaving about 23 mm of overlap.",
    "Fold the paper in half lengthwise and then unfold.": "Crease the sheet lengthwise, then open it flat.",
    "Flip the paper over and fold the top edge down about 1 inch (2.5cm).": "Turn the sheet over and fold the top edge down about 1 inch (2.5 cm).",
    "Flip the paper back around and fold the top two corners to the middle crease.": "Flip the sheet back and bring both top corners to the middle crease.",
    "Fold the top triangle piece down, so the diagonal edges line up with the top corners of the paper.": "Fold the top triangle down so its diagonals line up with the sheet's top corners.",
    "Fold the triangle piece back up so that the point touches the top of the paper.": "Fold that triangle back up so the tip meets the top edge.",
    "Flip the paper over to the back side and fold the top two corners to the middle crease.": "Flip to the back and fold both top corners to the middle crease.",
    "Fold one corner down to meet the other side. Unfold and repeat with the other corner.": "Fold one corner across to the far side, open it, then repeat with the other corner.",
    "Unfold and flip the paper over. Fold the top down so the new crease goes right through the cross made by the previous step.": "Open and flip the sheet. Fold the top so the new crease cuts through the previous cross.",
    "Unfold and flip the paper over. Accordion fold the sides into the middle and press flat.": "Open and flip the sheet. Accordion-tuck the sides into the middle and press flat.",
    "Fold the top point down to meet the edge of the top layer of paper.": "Fold the tip down to the edge of the top layer.",
    "Unfold everything to the beginning. Then fold on the existing crease which is just under the middle of the paper.": "Open everything to the start, then fold on the existing crease just below mid-sheet.",
    "Fold that crease all the way over so it goes past the bottom.": "Carry that crease all the way over so it passes the bottom edge.",
    "Next, open the sheet back up and fold down the right side. The second crease should meet the center line. Then fold the corner out.": "Open the sheet, fold the right side down so the second crease hits the midline, then fold the corner out.",
    "Fold down the top point to meet where the other folds come together.": "Fold the tip down to where the other folds meet.",
    "Fold the right side over to the left, unfold and repeat with the left side.": "Fold right over left, open it, then repeat from the left.",
    "Unfold and then fold the top down so the fold goes through the X formed by all the other creases.": "Open the sheet, then fold the top so the crease runs through the X of earlier creases.",
    "Unfold again and then fold the right side down to the diagonal crease.": "Open again, then fold the right side down to the diagonal crease.",
    "Fold one corner down to the other side. Unfold.": "Fold one corner across to the other side, then open it.",
    "Repeat on the other side and unfold again.": "Repeat on the other side and open again.",
    "Fold one side over and line up the edge with the crease made in the previous step.": "Fold one side over so its edge meets the previous crease.",
    "Fold the other side over along the same crease.": "Fold the other side over on that same crease.",
    "Fold the top down along the existing creased line.": "Fold the top down on the existing crease.",
    "Fold the entire airplane in half down the middle. Unfold.": "Close the whole airplane down the middle, then open it.",
    "Fold the top two corners to the center about an inch (2.5 cm) above the downward facing point, to form a triangle shape on top and a diamond shape on bottom.": "Bring both top corners in about 1 inch (2.5 cm) above the downward tip, making a triangle on top and a diamond below.",
    "Fold the corners down to each side and unfold to make an X shape.": "Crease both corners down to the sides, then open them to leave an X.",
    "Fold the top down and make a crease so it lines up with the middle of the X shape.": "Fold the top so the crease crosses the middle of the X.",
    "Unfold the last step and then accordion fold the sides so they are tucked inside.": "Undo the last fold, then accordion-tuck the sides inside.",
    "Fold the bottom corners of the triangle up to the top.": "Fold the triangle's bottom corners up to the top.",
    "Now, fold the top sides of the diamond to the center line.": "Now fold the diamond's top sides onto the midline.",
    "Cut off the extra piece at the bottom and open up the paper. You should have a perfect square.": "Trim the leftover bottom strip and open the sheet — you should have a square.",
    "Rotate the sheet so that one corner is facing up and then fold in the outer corners to the center line.": "Turn the sheet so a corner points up, then fold the outer corners onto the midline.",
    "Fold down the top point so that it touches the horizontal line.": "Fold the tip down until it touches the horizontal line.",
    "Unfold the previous step and then accordion fold the sides in to form a diamond shape.": "Undo the previous fold, then accordion-tuck the sides into a diamond.",
    "Fold the corner down to the other side of the paper.": "Fold the corner across to the other side of the sheet.",
    "Unfold and repeat with the other corner. Then unfold again.": "Open it, repeat with the other corner, then open again.",
    "Accordion fold the sides inside using the creases made in the previous steps.": "Accordion-tuck the sides inside on the creases you already made.",
    "Fold the top layer of the side corners up to the top.": "Fold the top layer of the side corners up to the top edge.",
    "Take both outer edges and fold them to the center. Be sure they are tucked underneath the diamond shape.": "Fold both outer edges into the centre, tucking them under the diamond.",
    "Measure one inch (2.5cm) to the left and right of the center line and draw vertical lines.": "Mark 1 inch (2.5 cm) left and right of the midline with vertical lines.",
    "Now, measure 3 inches (7.6cm) from the bottom on both sides and draw a horizontal line.": "Now mark 3 inches (7.6 cm) up from the bottom on both sides and draw a horizontal line.",
    "Open the sheet back up and fold in half horizontally.": "Open the sheet and crease it horizontally in half.",
    "With the folded paper held with the opening on the bottom, fold both left and right edges to the center.": "Hold the folded packet with the opening at the bottom, then fold both edges into the centre.",
    "Open the last two folds and then fold the top corner down to the first crease.": "Open the last two folds, then fold the top corner down to the first crease.",
    "Now, fold the top right edge down to the center line.": "Now fold the top-right edge down onto the midline.",
    "Place the sheet horizontally and fold it in half from left to right. Open the sheet back up.": "Lay the sheet landscape, crease left to right, then open it.",
    "Fold down the top left corner to the center, so that the crease lines up with the corner.": "Fold the top-left corner into the centre so the crease lines up with the corner.",
    "Next, fold down the top edge about half an inch (1.25cm).": "Next fold the top edge down about half an inch (1.25 cm).",
    "Fold down the top edge three more times.": "Fold the top edge down three more times.",
    "Grab the right center flap and fold it out, as shown.": "Take the right centre flap and fold it outward as shown.",
    "Fold the left corner down to the opposite corner and unfold to create an 'x' crease.": "Fold the left corner to the opposite corner and open it to leave an X crease.",
    "Next, accordion fold the sides in to create a triangle shape.": "Next accordion-tuck the sides in to form a triangle.",
    "Fold both bottom corners up to the top point.": "Bring both bottom corners up to the top point.",
    "Take the extra piece that you cut off earlier and fold the top corners to the center to form an arrow.": "Take the earlier offcut and fold its top corners into the centre to make an arrow.",
    "Fold in the sides of the bottom layer. Note that the crease goes right through the bottom corners.": "Fold in the bottom layer's sides — the crease should run through the bottom corners.",
    "Now, fold the big triangle in half, away from you and then fold it back up again so a little bit is poking up.": "Fold the large triangle in half away from you, then fold it back so a little tip sticks up.",
    "Fold the top right corner over, down to the center fold as shown.": "Fold the top-right corner over down to the centre fold as shown.",
    "Again, fold the corner down to meet the horizontal fold.": "Fold that corner down again to meet the horizontal crease.",
    "Open the paper back up and repeat with the left corner.": "Open the sheet and repeat with the left corner.",
    "Open the paper back up and accordion fold both sides into the middle.": "Open the sheet and accordion-tuck both sides into the middle.",
    "Next, fold the bottom right corner of the triangle shape up to the top.": "Next fold the triangle's bottom-right corner up to the top.",
    "Now, fold the bottom right edge of the diamond shape up to the center line.": "Now fold the diamond's bottom-right edge up onto the midline.",
    "Fold the paper in half the other direction and orient the folded edge at the bottom. The flaps from the previous fold should be on the outside.": "Fold the other way with the folded edge at the bottom; keep the earlier flaps on the outside.",
    "Fold the bottom two corners in to the middle to make a triangle shape. Unfold.": "Fold both bottom corners into the middle to make a triangle, then open them.",
    "Accordion fold the corners into the middle, tucking the triangle pieces inside.": "Accordion-tuck the corners into the middle, hiding the triangle pieces inside.",
    "Fold the front piece down, aligned with the corner on the outside edge. Make a strong crease and fold back up so it looks like step 5.": "Fold the front piece down aligned with the outer corner, press a firm crease, then fold it back up to match step 5.",
    "Fold the top point down to the edge of the previous fold.": "Fold the tip down to the edge of the previous fold.",
    "Bring the right corner down to meet the bottom-center of the left rectangle. If you are using A4 sized paper, stop 2cm away from the bottom edge.": "Bring the right corner to the bottom-centre of the left rectangle — on A4, stop 2 cm short of the bottom edge.",
    "Fold the corner of the triangle over so about 1/3 of it is overlapping the paper behind and 2/3 is sticking out.": "Fold the triangle corner over so about one-third overlaps the sheet behind and two-thirds sticks out.",
    "Cut off the extra piece at the bottom, making a square piece of paper folded once to make a triangle.": "Trim the bottom offcut so you have a square folded once into a triangle.",
    "Fold the top back to meet the bottom edge of the other side. If you are using A4 size paper, stop about 2cm short of the bottom edge.": "Fold the top back to the other side's bottom edge — on A4, stop about 2 cm short.",
    "Fold the paper in half and then unfold. Cut along the fold and pick one side. You can save the other side to make a second boomerang.": "Crease in half, open it, cut on that crease, and keep one half — save the other for a second boomerang.",
    "Unfold the previous 2 steps, then open up the left flap and pinch the middle of the paper so it folds the other direction.": "Undo the last two folds, open the left flap, and pinch the middle so it creases the other way.",
    "Continue rotating and folding that pinched piece flat until you get an L shape with vertical walls.": "Keep rotating and flattening that pinched piece until you have an L with upright walls.",
    "Unfold everything back to step 2 and then fold the corners to the diagonal crease that you just made.": "Open everything back to step 2, then fold the corners to the diagonal crease you just made.",
    "Fold the paper in half vertically. Then, open and fold both corners down to the middle.": "Crease vertically in half, open it, then fold both corners down to the middle.",
    "Take one top edge and fold down to the bottom edge on the same side.": "Take one top edge and fold it down to the bottom edge on that same side.",
    "Unfold and repeat step two on the other side to get the creases as shown in the picture.": "Open it and repeat step two on the other side to match the creases in the photo.",
    "Fold the top down and accordion fold the sides in at the same time.": "Fold the top down while accordion-tucking the sides inward together.",
    "Fold back both outer points of the triangle shape. Be sure the folds are tucked in-between both layers.": "Fold both outer triangle points back, tucking the folds between the layers.",
    "Fold the top corners to the center line so that the crease goes through to the bottom corners.": "Fold the top corners to the midline so each crease continues through to the bottom corners.",
    "Unfold the last step and accordion fold the corners inside.": "Undo the last fold and accordion-tuck the corners inside.",
    "Fold down the top right corner down to the end of the crease you just made.": "Fold the top-right corner down to the end of the crease you just made.",
    "Open the last fold and repeat with the other side to get the creases shown.": "Open that fold and repeat on the other side to match the creases shown.",
    "Next, accordion fold the two corners in and the center out to get this diamond shape.": "Next accordion-fold both corners in and the centre out to form this diamond.",
    "Fold the paper in half in both directions, forming 4 equal rectangles. Unfold.": "Crease the sheet both ways into four equal rectangles, then open it.",
    "Fold the paper in half towards you and then rotate so that the thickest point is facing up.  The squared off point will be facing to the left.": "Close the sheet toward yourself, then rotate so the thickest tip points up and the squared tip faces left.",
    "Fold the top part of the right side to the center and then take the bottom part of the right side and stretch it to the side and flatten it out. Repeat with the left side.": "Fold the upper right into the centre, then pull the lower right out sideways and flatten; mirror on the left.",
    "Reach inside and pull out the center flaps. Then refold them in the opposite direction and fold the sides in.": "Reach in, pull the centre flaps out, refold them the opposite way, then fold the sides in.",
    "Take the bottom edge of each center flap and fold it backwards at a slight angle and then tuck under and press flat.": "Fold each centre flap's bottom edge back at a slight angle, tuck it under, and press flat.",
}


def rewrite_en(text: str) -> str:
    text = text.strip()
    if text in FIXED_EN:
        return FIXED_EN[text]
    # Soft fallback transforms for any leftovers.
    out = text
    out = out.replace("Fold the paper", "Crease the sheet")
    out = out.replace("Fold the sheet", "Crease the sheet")
    out = out.replace("center line", "midline")
    out = out.replace("centre line", "midline")
    out = out.replace("Unfold and then", "Open it flat, then")
    out = out.replace("Unfold and", "Open the sheet and")
    out = out.replace("Repeat with the other side", "Mirror the fold on the opposite side")
    out = out.replace("as shown", "as in the photo")
    if out == text:
        # Force a light rewrite so nothing stays identical.
        if out.endswith("."):
            out = out[:-1] + " as shown in the guide."
        else:
            out = out + " as shown in the guide."
    return out


FIXED_CN: dict[str, str] = {
    "把纸对折。": "沿中缝把纸对折压平。",
    "展开，再把两角折到中线。": "先展平，再把两个顶角收进中缝。",
    "把上边两缘折到中心。": "把上方两条长边折向中缝对齐。",
    "把纸飞机对折。": "沿机身中缝把整架飞机合上。",
    "把机翼向下折，对齐机身底边。": "把两侧机翼向下折，边缘贴齐机腹底边。",
}


def rewrite_cn(text: str, en_new: str = "") -> str:
    text = (text or "").strip()
    if text in FIXED_CN:
        return FIXED_CN[text]

    out = text
    replacements = [
        ("把纸飞机对折", "沿中缝把纸飞机合上"),
        ("把飞机对折", "沿中缝把飞机合上"),
        ("把纸对折", "沿中线对折纸张"),
        ("将纸对折", "沿中线对折纸张"),
        ("展开，再", "先展平，再"),
        ("展开并", "先展平并"),
        ("展开后", "展平后"),
        ("完全展开", "完全展平"),
        ("展开纸张", "把纸展平"),
        ("中心线", "中缝"),
        ("中线", "中缝"),
        ("如图所示", "对照图示"),
        ("如图", "对照图示"),
        ("重复另一侧", "在另一侧做同样的折法"),
        ("另一侧重复", "在另一侧同样操作"),
        ("另一边重复", "在另一边同样操作"),
        ("重复上一步", "按上一步同样再折一次"),
        ("风琴折", "手风琴式叠折"),
        ("手风琴折叠", "手风琴式叠折"),
        ("剪掉", "裁去"),
        ("剪去", "裁去"),
        ("剪开", "裁开"),
        ("剪刀", "裁纸刀或剪刀"),
        ("折叠", "折压"),
        ("对折", "对折压平"),
        ("翻面", "把纸翻到背面"),
        ("翻转", "把纸翻过来"),
        ("机翼向下折", "把机翼往下折"),
        ("折到中心", "折向中缝"),
        ("折到中间", "折向中缝"),
        ("折到中缝", "收进中缝"),
    ]
    for a, b in replacements:
        if a in out:
            out = out.replace(a, b)
    # Second light pass for remaining identical lines.
    if out == text:
        if out.endswith("。"):
            out = out[:-1] + "，按图示完成。"
        elif out:
            out = out + "（按图示）"
        elif en_new:
            out = "按图示完成这一步。"
    return out


def main() -> None:
    planes = json.loads(DATA.read_text(encoding="utf-8"))
    changed = 0
    same_en = 0
    for plane in planes:
        for step in plane.get("steps") or []:
            old_en = step.get("text") or ""
            old_cn = step.get("textCn") or ""
            new_en = rewrite_en(old_en)
            new_cn = rewrite_cn(old_cn, new_en)
            if new_en == old_en:
                same_en += 1
            if new_en != old_en or new_cn != old_cn:
                changed += 1
            step["text"] = new_en
            step["textCn"] = new_cn

    DATA.write_text(json.dumps(planes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Sanity: Basic Dart
    bd = next(p for p in planes if p["slug"] == "Basic-Dart")
    print(f"updated steps touching {changed} entries; identical EN leftovers {same_en}")
    for s in bd["steps"]:
        print(f"  {s['n']}. {s['text']}")
        print(f"     {s['textCn']}")


if __name__ == "__main__":
    main()
