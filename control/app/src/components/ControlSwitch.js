/*\
|*|  :: Bootstrap Switch Button ::
|*|
|*|  Bootstrap Switch Button (React)
|*|  https://github.com/gitbrent/bootstrap-switch-button-react
|*|
|*|  This library is released under the MIT Public License (MIT)
|*|
|*|  Bootstrap Switch Button (C) 2019-present Brent Ely (https://github.com/gitbrent)
|*|
|*|  Permission is hereby granted, free of charge, to any person obtaining a copy
|*|  of this software and associated documentation files (the "Software"), to deal
|*|  in the Software without restriction, including without limitation the rights
|*|  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
|*|  copies of the Software, and to permit persons to whom the Software is
|*|  furnished to do so, subject to the following conditions:
|*|
|*|  The above copyright notice and this permission notice shall be included in all
|*|  copies or substantial portions of the Software.
|*|
|*|  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
|*|  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
|*|  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
|*|  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
|*|  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
|*|  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
|*|  SOFTWARE.
\*/

import React, {useEffect, useState} from 'react';
import './ControlSwitch.css';
import classNames from "classnames";

const ControlSwitch = ({
	checked: defaultChecked,
	onChange,
	disabled,
	onlabel,
	offlabel,
	onstyle,
	offstyle,
	size,
	className,
	width,
	height,
    title,
}) => {
	const [checked, setChecked] = useState(defaultChecked);

	useEffect(() => {
		setChecked(defaultChecked);
	}, [defaultChecked]);

	const toggle = event => {
		if (!disabled) {
			const newState = !checked;

			setChecked(newState);
			onChange(newState);
		}

		event.stopPropagation();
	};

	let switchStyle = {};
	if (width) {
		switchStyle.width = width;
	} // else {
    //     switchStyle.width = "100%";
    // }

	if (height) {
		switchStyle.height = height; // + 'px';
	}

	let labelStyle = {};
	if (height) {
		labelStyle.lineHeight = 'calc(' + height + 'px * 0.8)';
	}

	return (
        <div>
        <label htmlFor={title}>{title}:&nbsp;</label>
		<div
            id={title}
			className={classNames(
				'switch btn',
				(checked ? 'on btn-' + onstyle : 'off btn-' + offstyle),
				(size ? 'btn-' + size : ''),
				className || ''
			)}
			style={switchStyle}
			onClick={toggle}
		>
			<div className="switch-group">
				<span
					className={classNames(
						'switch-on btn',
						'btn-' + onstyle,
						(size ? 'btn-' + size : '')
					)}
					style={labelStyle}
				>
					{onlabel}
				</span>
				<span
					className={classNames(
						'switch-off btn',
						'btn-' + offstyle,
						(size ? 'btn-' + size : '')
					)}
					style={labelStyle}
				>
					{offlabel}
				</span>
				<span
					className={classNames(
						'switch-handle btn btn-light',
						(size ? 'btn-' + size : '')
					)}
				/>
			</div>
		</div>
        </div>
	);
};

ControlSwitch.defaultProps = {
	checked: false,
	onChange: () => {},
	disabled: false,
	onlabel: 'On',
	offlabel: 'Off',
	onstyle: 'primary',
	offstyle: 'light',
	className: '',
    title: '',
};

export default ControlSwitch;