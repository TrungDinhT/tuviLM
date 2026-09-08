import "server-only";

import { mongodbAdapter } from "@better-auth/mongo-adapter";
import { betterAuth } from "better-auth";
import { MongoClient } from "mongodb";

const mongoUri = process.env.MONGODB_URI ?? "mongodb://localhost:27017";
const mongoDatabase = process.env.MONGODB_DATABASE ?? "tuvilm";

const globalMongo = globalThis as typeof globalThis & {
  tuviAuthMongoClient?: MongoClient;
};

const mongoClient = globalMongo.tuviAuthMongoClient ?? new MongoClient(mongoUri);
if (process.env.NODE_ENV !== "production") globalMongo.tuviAuthMongoClient = mongoClient;

const googleClientId = process.env.GOOGLE_CLIENT_ID;
const googleClientSecret = process.env.GOOGLE_CLIENT_SECRET;
const googleConfigured = Boolean(googleClientId && googleClientSecret);

export const auth = betterAuth({
  appName: "TuviLM",
  baseURL: process.env.BETTER_AUTH_URL,
  secret: process.env.BETTER_AUTH_SECRET,
  database: mongodbAdapter(mongoClient.db(mongoDatabase), {
    client: mongoClient,
    // Works with both a standalone local MongoDB and a replica set.
    transaction: false,
  }),
  emailAndPassword: {
    enabled: true,
  },
  socialProviders: googleConfigured
    ? {
        google: {
          clientId: googleClientId as string,
          clientSecret: googleClientSecret as string,
          prompt: "select_account",
        },
      }
    : {},
});
