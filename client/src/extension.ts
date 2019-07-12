/* --------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for license information.
 * ------------------------------------------------------------------------------------------ */
'use strict';
import * as path from 'path';

import { ExtensionContext, workspace, StatusBarItem, window, StatusBarAlignment, commands, ConfigurationTarget} from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions} from 'vscode-languageclient';

let serverPath: string;
let languageClient: LanguageClient;
let kvLangStatusBar: StatusBarItem;
let kvLangPythonPath: string; // Last path which was used to activate Language server

function createLanguageClient(command: string, serverArgs: string[]): LanguageClient {
	const serverOptions: ServerOptions = {
		run : { command: command, args: serverArgs },
		debug: { command: command, args: serverArgs }
	};
	const clientOptions: LanguageClientOptions = {
		documentSelector: [{scheme: 'file', language: 'kv'},
		                   {scheme: 'file', language: 'python'}]
	}
	return new LanguageClient('kvls', 'KvLang Server', serverOptions, clientOptions, false);
}

export function activate(context: ExtensionContext) {
	serverPath = context.asAbsolutePath(path.join('server', 'server.py'));
	kvLangPythonPath = getPythonPath();
	languageClient = createLanguageClient(kvLangPythonPath, [serverPath]);
	languageClient.start();

	const myCommandId = 'KvLang.showPythonPathSelection';
	kvLangStatusBar = window.createStatusBarItem(StatusBarAlignment.Left, 0);
	kvLangStatusBar.text = 'KvLang Python';
	kvLangStatusBar.tooltip = kvLangPythonPath;
	kvLangStatusBar.command = myCommandId;
	kvLangStatusBar.show();

	workspace.onDidChangeConfiguration(restartLanguageServer);
	commands.registerCommand(myCommandId, updatePythonPath);
	console.log('KvLang: Activating of extension is finished with success')
}

export function deactivate(): Thenable<void> {
	if (!languageClient) {
		console.log('KvLang: Deactivation of extension is finished. Language Client is undefined')
		return undefined;
	}
	console.log('KvLang: Deactivation of extension is finished with success')
	return languageClient.stop();
}

function restartLanguageServer(): void {
	let pythonPath = getPythonPath();
	if (kvLangPythonPath != pythonPath) {
		console.log('KvLang: Restart of language server ongoing. Python path has been changed')
		kvLangStatusBar.tooltip = pythonPath;

		// Deactivate language client
		if (languageClient) {
			languageClient.stop();
		}

		// Start new language client with new path
		kvLangPythonPath = pythonPath;
		languageClient = createLanguageClient(pythonPath, [serverPath]);
		languageClient.start();
	}
}

function updatePythonPath(): void {
	let options = {prompt: 'Change python path for the KvLang Language Server. \
	                        Empty input will clear current configuration.',
	               placeHolder: 'current: ' + getPythonPath()};
    window.showInputBox(options).then(input => {

		input = input.trim();
		let pythonPath: string;
		if (input === '') {
			pythonPath = 'python';
			input = undefined;
		} else {
			pythonPath = input;
		}

		// Update configuration
		const configuration = workspace.getConfiguration('kvlang', null);
		let folder = workspace.getWorkspaceFolder(window.activeTextEditor.document.uri);
		if (folder === undefined && workspace.workspaceFolders === undefined) {
			console.log('KvLang: Updating global configuration: input=%s, pythonPath=%s', input, pythonPath)
			configuration.update('pythonPath', input, ConfigurationTarget.Global);
		} else {
			console.log('KvLang: Updating workspace configuration: input=%s, pythonPath=%s', input, pythonPath)
			configuration.update('pythonPath', input, ConfigurationTarget.Workspace);
		}
	});
}

function getPythonPath(): string {
	const configuration = workspace.getConfiguration('kvlang', null);
	let pythonPath = configuration.get('pythonPath', undefined);

	if (pythonPath === undefined) {
		console.error('KvLang: PythonPath is undefined. Assigned default value of python path')
		pythonPath = 'python';
	}
	return pythonPath;
}
