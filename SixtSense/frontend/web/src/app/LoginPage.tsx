import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";

// import { AlertCircleIcon, CheckCircleIcon } from 'lucide-react';

// import { LoginForm } from '@/components/auth/LoginForm';
// import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: { preventDefault: () => void }) => {
    e.preventDefault();
    console.log("Login submitted", { email, password });
  };

  return (
    // <div className="flex min-h-[calc(100vh-3rem)] w-full items-center justify-center p-6 md:p-10 bg-muted">
    //   <div className="w-full max-w-sm">
    //     {error !== '' && (
    //       <div className="mb-10 shadow-sm rounded-xl">
    //         <Alert variant="destructive">
    //           <AlertCircleIcon />
    //           <AlertTitle>Sign in failed, please try again.</AlertTitle>
    //           <AlertDescription>
    //             <p>{error}</p>
    //           </AlertDescription>
    //         </Alert>
    //       </div>
    //     )}
    //     {confirm !== '' && (
    //       <div className="mb-10 shadow-sm rounded-xl">
    //         <Alert variant="default">
    //           <CheckCircleIcon />
    //           <AlertTitle>
    //             {confirm === '1' ? 'Sign up successful.' : 'Account activated.'}
    //           </AlertTitle>
    //           <AlertDescription>
    //             <p>
    //               {confirm === '1'
    //                 ? 'Please confirm your address by clicking on the link in the E-Mail we just sent you. Afterwards you can login into your account.'
    //                 : 'Your account is now active. Please login with the credentials you provided during registration.'}
    //             </p>
    //           </AlertDescription>
    //         </Alert>
    //       </div>
    //     )}
    //     <LoginForm />
    //   </div>
    // </div>
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <Card className="w-full max-w-sm shadow-xl rounded-2xl">
          <CardContent className="p-6 space-y-6">
            <h1 className="text-2xl font-bold text-center">Login</h1>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Password
                </label>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>
              <Button type="submit" className="w-full rounded-xl py-2">
                Sign In
              </Button>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
