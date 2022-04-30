import { Overlay } from '../../components/Overlay.js';

/**
 * The HelpOverlay class definition.
 *
 * @author Stefan Glaser
 */
class HelpOverlay extends Overlay
{
	/**
	 * HelpOverlay Constructor
	 */
	constructor ()
	{
	  super('help-pane centered');

	  this.innerElement.innerHTML = '<h1>HELP...</h1><h4>I need somebody...</h4>';
	}
}

export { HelpOverlay };
