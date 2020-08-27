# Neural audio styling
<hr>
This project was made as part of the annual course work of the first year of study at the higher school of Economics.
<hr>
# Description
The goal of this work was to develop an algorithm for transferring the audio style of one music track to another. Two formats were considered as audio tracks-wav and midi.

<hr>
# *.WAV style transform

For wav files, I used algorithms for style transform for images (which have been sufficiently studied). And in order to apply them successfully, I used the Fourier transform to get the track spectrum, which can be interpreted as an image. Then I used the obtained spectra as input data for the style transform algorithm.
