import React from 'react';

import UniSignIn from './uni/components/sign-in';
import UniBox from './uni/components/primitives/box';
import { UniTypography as UT } from './uni/components/primitives/typography';

import UniFade from './uni/components/animations/fade';
import { useUniLogin } from './uni/api/hooks/login';
import { APP_NAME } from './data/config';
import UniStack from './uni/components/primitives/stack';


export default function AppPublic() {
  const [login, loading] = useUniLogin()


  return <UniFade show>
    <UniSignIn
      langSelector
      themeSelector
      lightBgImage=""
      email
      onLogin={login}
      loading={loading.loading}

      footerComponent={
        <>
          <UniBox.VHC fullWidth sx={{ p: 1, borderTop: "1px solid", borderColor: "divider" }}>
            <UT.Text small>© Copyright UNI {new Date().getFullYear()}</UT.Text>
          </UniBox.VHC>
        </>
      }

      headerComponent={
        <UniStack.Row spacing={2} sx={{ alignContent: "center", alignItems: "center" }}>
          <UniBox.VHC fullWidth fullHeight>
            <UT.Title large>{APP_NAME}</UT.Title>
          </UniBox.VHC>
        </UniStack.Row>
      }
    />
  </UniFade>
}