#!/bin/bash
echo "⏳ Waiting for MongoDB to be ready..."
until mongosh --host mongo --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
  sleep 2
done

echo "🚀 Restoring MongoDB dump..."
mongorestore --host mongo --drop --dir=/dump

echo "✅ Restore complete."
