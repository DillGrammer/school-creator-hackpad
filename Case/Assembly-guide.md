# Hackpad case

A simple rounded base and one removable cover, with six MX openings, a clickable encoder, an OLED recess and a USB-C opening. No foam, gaskets or damping layers are used.

## Files

- **Base.stl** and **Cover.stl**: the two main printed parts, already oriented for printing.
- **Knob.stl**: optional printed knob for a nominal 6 mm D-shaped EC11 shaft.
- **Hackpad_Case.step**: assembled solid model that can be opened in Fusion. Separate STEP files are also included.
- **Fit_coupon.stl**: optional small test of the MX opening and heat-set insert fit. It is a test piece, not part of the final case.

**Revision 1.1:** `Hackpad_Case.f3d` is the native Fusion model with editable base/cover features. The knob is centered over the encoder with its bottom at 30.9 mm, 0.8 mm above the hood. The CAD Y axis is the negative of KiCad top-view Y, so the encoder is top-left and OLED to its right. Replace earlier case files and archives; those had an incorrect handedness and native knob placement.

## Hardware

Use four M3 × 16 mm screws and four M3 heat-set inserts (assumed 5 mm outside diameter × 4 mm length). The screw recesses allow heads up to 5.7 mm diameter and 3.0 mm high. The insert pilot holes are 4.6 mm diameter and 4.2 mm deep. Install the inserts flush or slightly below the top of each base post.

The case matches the supplied Hackpad PCB revision 1.0: 86.5 × 88.5 mm, 1.6 mm thick, with mounting holes at (4.5,4.5), (82,29.5), (4.5,84), (82,84) mm. Case size is **92.1 × 94.1 mm**, 21.1 mm tall at the key plate and 30.1 mm at the control hood, excluding keys and knob.

## Assembly order

1. Remove print supports and test the switch and insert fit. Install the four heat-set inserts in the base **before fitting the PCB**.
2. Solder the XIAO directly to the PCB; fit the EC11 and OLED. The case assumes an OLED underside 8.5 mm above the main PCB, and a module up to 38 × 12 mm.
3. Snap the six MX switches into the cover from above. **Do this before soldering the switches to the PCB**; an assembled switch's upper flange cannot pass through the plate opening.
4. Bring the PCB up underneath the cover, align the six sets of switch pins, encoder shaft and OLED opening, then solder the switch pins from below.
5. Place that assembly into the base. Install the four M3 × 16 mm screws through the cover and PCB into the base inserts; tighten gently. The lower screw heads sit flush with the key plate. The upper two are reached through the recessed screw wells.
6. Fit the keycaps. If using the printed knob, align its D-shaped socket and leave **at least 0.8 mm between knob and hood** so the encoder can still be pressed. Do not force the knob fully down against the hood.

The cover comes off with four screws for later access. There are no loose internal spacers.

## Printing

A practical starting point is PLA, a 0.4 mm nozzle, 0.2 mm layers, four walls and 25–35% infill. The switch plate is 1.5 mm thick; switch openings are 14.2 mm square.

- Base.stl is bottom-down. Supports are generally unnecessary except if the printer needs help at the USB cutout.
- Cover.stl is already upside-down with the control roof toward the bed. **Enable supports from the build plate under the elevated key-plate area.** Keep support material out of the small holes when the slicer allows it. Remove supports before assembly.
- Knob.stl is socket-down; its internal roof is a short bridge.

The two colours in the preview are only a suggestion: print the base dark and cover light, or use one colour.

## Checks and fit assumptions

Each printable item is one valid CAD solid. Exported meshes have zero boundary/non-manifold edges. The modeled PCB, switches, OLED, encoder, screws and inserts have no volumetric collisions with the case. Reports are included.

Physical printing and assembly have not been tested. Before printing the full case, confirm the kit's insert dimensions, encoder shaft shape/height, OLED header height and screw head dimensions. The XIAO must be directly soldered; tall header sockets would need a case adjustment. The printed knob is optional because EC11 shaft variants differ. The preview uses illustrative keycaps and display glass.

## Additional reproducible files

`Hackpad_Assembly.step` contains the actual base, cover and optional knob with 0.8 mm click clearance, plus explicitly named REFERENCE component envelopes. The reference blocks are not manufacturer component models. Use the PCB files and component specifications for exact pin geometry.

`FusionBuild/FusionBuild.py` is the corrected native Fusion builder. Its base and cover dimensions match the checked STEP parts. In a new empty **Hybrid design**, open Scripts and Add-Ins and select this script folder, then run it. It creates editable base/cover features and imports the optional knob solid, exporting `Hackpad_Case.f3d` and a geometry report into this Case folder. The corrected script has executed successfully. Native solid volumes match the separate STEP geometry; its export includes a checked knob position. Do not use the older script in the working directory.
