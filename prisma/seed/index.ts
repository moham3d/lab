import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  const hashedPassword = await bcrypt.hash('password123', 10)

  // Create test users
  const users = await Promise.all([
    prisma.user.create({
      data: {
        username: 'nurse1',
        email: 'nurse1@hospital.com',
        fullName: 'Sarah Johnson',
        password: hashedPassword,
        role: 'NURSE',
      },
    }),
    prisma.user.create({
      data: {
        username: 'physician1',
        email: 'physician1@hospital.com',
        fullName: 'Dr. Michael Chen',
        password: hashedPassword,
        role: 'PHYSICIAN',
      },
    }),
    prisma.user.create({
      data: {
        username: 'admin1',
        email: 'admin1@hospital.com',
        fullName: 'Admin User',
        password: hashedPassword,
        role: 'ADMIN',
      },
    }),
  ])

  // Create test patients
  const patients = await Promise.all([
    prisma.patient.create({
      data: {
        ssn: '12345678901234',
        mobileNumber: '01123456789',
        fullName: 'Ahmed Mohamed',
        dateOfBirth: new Date('1985-05-15'),
        gender: 'MALE',
        address: '123 Cairo Street, Cairo, Egypt',
      },
    }),
    prisma.patient.create({
      data: {
        ssn: '23456789012345',
        mobileNumber: '01234567890',
        fullName: 'Fatma Ali',
        dateOfBirth: new Date('1990-08-22'),
        gender: 'FEMALE',
        address: '456 Alexandria Road, Alexandria, Egypt',
      },
    }),
  ])

  console.log('Seed data created successfully!')
  console.log('Users:', users.map(u => ({ username: u.username, role: u.role })))
  console.log('Patients:', patients.map(p => ({ ssn: p.ssn, name: p.fullName })))
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })