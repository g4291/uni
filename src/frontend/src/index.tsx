import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import '@fontsource/inter';

import UniTheme from './uni/theme';
import UniTranslator from './uni/translator';
import UniApi from './uni/api/api';
import UniToaster from './uni/components/toaster';
import AppPublic from './app-public';
import AppPrivate from './app-private';
import { translations } from './data/translations';
import { themeOptions } from './data/theme';
import { SERVER_URL } from './data/config';
import * as swr from './register-service-worker';
import { AppProvider } from './context/app';

swr.register();

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <UniTranslator.Provider defaultLanguage="CZ" translations={translations}>
      <UniTheme.Provider themeOptions={themeOptions}>
        <UniApi.Provider
          serverUrl={SERVER_URL}
          noAuthComponent={<AppPublic />}
        >
          <AppProvider>
            <AppPrivate />
          </AppProvider>
        </UniApi.Provider>
        <UniToaster small />
      </UniTheme.Provider>
    </UniTranslator.Provider>
    </React.StrictMode>
);
