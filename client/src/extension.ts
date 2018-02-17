/* --------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for license information.
 * ------------------------------------------------------------------------------------------ */
'use strict';
import * as path from 'path';

import { Disposable, ExtensionContext, workspace } from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions} from 'vscode-languageclient';

function startLangServer(command: string, serverModule: string[]): Disposable {

	const serverOptions: ServerOptions = {
		run : { command: command, args: serverModule },
		debug: { command: command, args: serverModule }
	};
	const clientOptions: LanguageClientOptions = {
		documentSelector: [{scheme: 'file', language: 'kv'}]
	}
	return new LanguageClient("kvls", "KvLang Server", serverOptions, clientOptions, false).start();
}

export function activate(context: ExtensionContext) {
	// Get KvLang configuration
	const configuration = workspace.getConfiguration();
	// Read value from configuration parameter
	const pythonCommand = configuration.get('kvlang.pythonCommand', "python");
	let serverModule = context.asAbsolutePath(path.join('server', 'server.py'));
	let disposable = startLangServer(pythonCommand, [serverModule]);
	context.subscriptions.push(disposable);
}
